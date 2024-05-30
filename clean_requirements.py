import re

# Read the content of the requirements.txt file
with open('requirements.txt', 'r') as file:
    lines = file.readlines()

# Process each line to remove the version numbers
cleaned_lines = [re.sub(r'==.*', '', line) for line in lines]

# Write the cleaned lines back to the requirements.txt file
with open('requirements.txt', 'w') as file:
    file.writelines(cleaned_lines)

print("Version numbers removed successfully.")
