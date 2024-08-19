import os
import shutil
from collections import defaultdict

# Define the paths
original_package_use_file = '/etc/portage/package.use'
script_directory = os.path.dirname(os.path.abspath(__file__))
copy_package_use_file = os.path.join(script_directory, 'package.use_copy')
package_use_dir = os.path.join(script_directory, 'package.use')

# Clean up any existing files from previous runs
if os.path.exists(copy_package_use_file):
    os.remove(copy_package_use_file)

if os.path.exists(package_use_dir):
    shutil.rmtree(package_use_dir)

# Create a copy of the original package.use file in the script directory
shutil.copyfile(original_package_use_file, copy_package_use_file)

# Ensure the local package.use directory exists
os.makedirs(package_use_dir)

# Dictionary to store consolidated USE flags for each package
package_flags = {}

# Open the copied package.use file
with open(copy_package_use_file, 'r') as f:
    lines = f.readlines()

# Process each line and consolidate USE flags for each package
for line in lines:
    # Skip empty lines or comments
    if line.strip() == '' or line.strip().startswith('#'):
        continue
    
    # Split the package name from the USE flags
    parts = line.strip().split()
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
    
    with open(package_file, 'w') as pf:
        pf.write(f"{package_name} {use_flags}\n")

# Verification Step
def reconstruct_package_use():
    reconstructed_lines = []
    
    # Reconstruct the package.use file from the local directory
    for package_file in os.listdir(package_use_dir):
        package_name = package_file.replace('_', '/')
        with open(os.path.join(package_use_dir, package_file), 'r') as pf:
            for line in pf:
                reconstructed_lines.append(line.strip())
    
    # Sort lines for consistent comparison
    return sorted(reconstructed_lines)

def verify_package_use():
    # Read and sort original package.use_copy file
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

# Run the verification
verify_package_use()

def cleanup_generated_files():
    print("Cleaning up generated files...")
    if os.path.exists(copy_package_use_file):
        os.remove(copy_package_use_file)
    if os.path.exists(package_use_dir):
        shutil.rmtree(package_use_dir)
    print("Cleanup complete.")

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

# Prompt the user to commit the changes
def prompt_commit_changes():
    while True:
        user_input = input("Do you want to commit these changes? (yes/y or no/n): ").strip().lower()
        if user_input in ['yes', 'y']:
            print("Committing the changes...")
            commit_changes()
            break
        elif user_input in ['no', 'n']:
            print("Changes were not committed.")
            cleanup_generated_files()
            break
        else:
            print("Invalid input. Please type 'yes/y' or 'no/n'.")

# Call the commit prompt function
prompt_commit_changes()