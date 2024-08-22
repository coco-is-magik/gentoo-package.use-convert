# Gentoo package.use Converter

This script converts a Gentoo Linux package.use file into a directory format where each package has its own file.
This can help manage complex USE flag configurations by organizing them into separate, easily editable files.
The script also verifies that the conversion process preserves the original USE flag configurations, allowing you to review any changes before committing them.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Error Handling](#error-handling)
- [License](#license)

## Features

- Converts a package.use file to a directory format: Each package will have its own file in the package.use/ directory.
- Verifies the conversion: The script compares the original package.use file with the reconstructed configuration to ensure accuracy.
- Interactive commit: After verification, the script prompts you to commit the changes, allowing you to review the output before any modifications are made.
- Dry run option: You can run the script in dry-run mode to see what changes would be made without actually modifying the system.
- Color-coded output: Missing flags are shown in red, and newly added flags are shown in green for easy identification.

## Requirements

- Python 3.x: The script is written in Python and requires Python 3 to run.
- Gentoo Linux: This script is designed specifically for Gentoo Linux and will not work on other distributions or operating systems.

## Dependencies

This script uses only Python's standard library and does not require any additional packages to be installed via pip. Ensure you have Python 3.x installed on your system.

## Installation

Clone the repository (if applicable):
```
git clone https://github.com/yourusername/gentoo-package-use-converter.git
cd gentoo-package-use-converter
```
Ensure Python 3.x is installed:
```
python3 --version
```

## Usage
### Basic Usage

Run the script with default settings:
```
sudo python3 gentooscript.py
```
This will:
- Copy your existing package.use file to a backup in the script directory.
- Convert the package.use file into a directory format.
- Verify the conversion by comparing the original file with the reconstructed configuration.
- Prompt you to commit the changes.

### Dry Run

To see what changes would be made without modifying your system:
```
python3 gentooscript.py --dry-run
```
## Error Handling

The script includes robust error handling to manage common issues such as:

- Missing package.use file
- Existing package.use directory
- Permission errors

If any errors occur, the script will display a helpful message and clean up any temporary files.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
