import os
import shutil
import datetime
import argparse
from collections import defaultdict

# Define the paths
original_package_use_file = '/etc/portage/package.use'
script_directory = os.path.dirname(os.path.abspath(__file__))
copy_package_use_file = os.path.join(script_directory, 'package.use_copy')
package_use_dir = os.path.join(script_directory, 'package.use')

def cleanup_generated_files():
    """Clean up any generated files from the current run."""
    print("Cleaning up generated files...")
    if os.path.exists(copy_package_use_file):
        os.remove(copy_package_use_file)
    if os.path.exists(package_use_dir):
        shutil.rmtree(package_use_dir)
    print("Cleanup complete.")

def handle_error(message):
    """Handle errors by displaying a message, cleaning up, and exiting."""
    print(f"Error: {message}")
    cleanup_generated_files()
    exit(1)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process package.use file into a directory format.")
    parser.add_argument('--dry-run', action='store_true', help="Run the script without making any changes.")
    return parser.parse_args()

def main():
    args = parse_args()

    # Initial checks and setup
    if not os.path.exists(original_package_use_file):
        handle_error(f"Original package.use file not found at {original_package_use_file}")
    
    if os.path.isdir(original_package_use_file):
        handle_error("An existing package.use directory was detected. The script is designed to work only with a package.use file. Please remove or rename the directory and try again.")
    
    cleanup_generated_files()

    try:
        shutil.copyfile(original_package_use_file, copy_package_use_file)
    except Exception as e:
        handle_error(f"Failed to copy the original package.use file: {e}")

    try:
        os.makedirs(package_use_dir)
    except Exception as e:
        handle_error(f"Failed to create package.use directory: {e}")

    # Dictionary to store consolidated USE flags for each package
    package_flags = {}

    # Open the copied package.use file and process its contents
    try:
        with open(copy_package_use_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Skip empty lines or comments
            if line.strip() == '' or line.strip().startswith('#'):
                continue
            
            # Split the package name from the USE flags
            parts = line.strip().split()
            if len(parts) < 2:
                print(f"Warning: Invalid line format found: '{line.strip()}'")
                continue
            
            package_name = parts[0]
            use_flags = ' '.join(parts[1:])
            
            # Consolidate USE flags for each package
            if package_name in package_flags:
                existing_flags = set(package_flags[package_name].split())
                new_flags = set(use_flags.split())
                combined_flags = existing_flags.union(new_flags)
                package_flags[package_name] = ' '.join(sorted(combined_flags))
            else:
                package_flags[package_name] = use_flags

        # Write the consolidated USE flags to separate files
        for package_name, use_flags in package_flags.items():
            package_file = os.path.join(package_use_dir, package_name.replace('/', '_'))
            
            try:
                with open(package_file, 'w') as pf:
                    pf.write(f"{package_name} {use_flags}\n")
            except Exception as e:
                handle_error(f"Failed to write to file {package_file}: {e}")
    except Exception as e:
        handle_error(f"Failed to process the package.use file: {e}")

    # Verification Step
    def reconstruct_package_use():
        reconstructed_lines = []
        
        try:
            # Reconstruct the package.use file from the local directory
            for package_file in os.listdir(package_use_dir):
                package_name = package_file.replace('_', '/')
                with open(os.path.join(package_use_dir, package_file), 'r') as pf:
                    for line in pf:
                        reconstructed_lines.append(line.strip())
        except Exception as e:
            handle_error(f"Failed to reconstruct package.use from directory: {e}")
        
        # Sort lines for consistent comparison
        return sorted(reconstructed_lines)

    def verify_package_use():
        # Read and sort original package.use_copy file
        try:
            with open(copy_package_use_file, 'r') as f:
                original_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            
            original_lines = sorted(original_lines)
            
            # Reconstruct and sort the package.use file from the created directory
            reconstructed_lines = reconstruct_package_use()
            
            # Compare the original lines with the reconstructed lines
            if original_lines == reconstructed_lines:
                print("Verification passed: The package.use directory matches the original package.use file.")
            else:
                print("Verification failed: Differences found between the package.use directory and the original package.use file.")
                print("\nDifferences:")
                print("\n\nOriginal -> Reconstruct")
                
                # Create dictionaries to map package names to their USE flags
                original_dict = {line.split()[0]: set(line.split()[1:]) for line in original_lines}
                reconstructed_dict = {line.split()[0]: set(line.split()[1:]) for line in reconstructed_lines}
                
                # ANSI escape codes for coloring
                RED = '\033[91m'
                GREEN = '\033[92m'
                RESET = '\033[0m'
                
                # Find differences
                all_packages = set(original_dict.keys()).union(reconstructed_dict.keys())
                
                for package in sorted(all_packages):
                    original_flags = original_dict.get(package, set())
                    reconstructed_flags = reconstructed_dict.get(package, set())
                    
                    if original_flags != reconstructed_flags:
                        # Identify missing and new flags
                        missing_flags = original_flags - reconstructed_flags
                        added_flags = reconstructed_flags - original_flags
                        
                        # Mark missing and new flags with colors
                        marked_original_flags = ' '.join(sorted([f"{RED}-{flag}{RESET}" for flag in missing_flags] + [flag for flag in original_flags]))
                        marked_reconstructed_flags = ' '.join(sorted([f"{GREEN}*{flag}{RESET}" for flag in added_flags] + [flag for flag in reconstructed_flags if flag not in added_flags]))
                        
                        print(f"{package} {marked_original_flags} -> {package} {marked_reconstructed_flags}")
        except Exception as e:
            handle_error(f"Failed during verification: {e}")

    # Commit Function
    def commit_changes():
        try:
            print("Committing the changes...")
            
            # Remove the original package.use file
            if os.path.exists(original_package_use_file):
                os.remove(original_package_use_file)
            
            # Move the generated package.use directory to the original location
            shutil.move(package_use_dir, os.path.dirname(original_package_use_file))
            
            print(f"Changes committed. The original package.use file has been backed up as {copy_package_use_file}.")
        except PermissionError:
            print("Permission Denied: You do not have the necessary permissions to make changes to /etc/portage/package.use.")
            print("Please run the script with appropriate permissions (e.g., using sudo) and try again.")
            cleanup_generated_files()
        except Exception as e:
            handle_error(f"Failed to commit changes: {e}")

    # Prompt the user to commit the changes
    def prompt_commit_changes():
        while True:
            user_input = input("Do you want to commit these changes? (yes/y or no/n): ").strip().lower()
            if user_input in ['yes', 'y']:
                commit_changes()
                break
            elif user_input in ['no', 'n']:
                print("Changes were not committed.")
                cleanup_generated_files()
                break
            else:
                print("Invalid input. Please type 'yes/y' or 'no/n'.")

    # Run the verification
    verify_package_use()

    # Call the commit prompt function
    if args.dry_run:
        print("Dry run complete. No changes were made.")
    else:
        prompt_commit_changes()


if __name__ == "__main__":
    main()