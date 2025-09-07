import json
import os

file_path = "assets/description.json"

# Load existing file if it exists, else start with empty dict
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
else:
    data = {}

print("Add a new description for an upgrade")
print("Enter the upgrade level")
level = input().strip()
print("Enter the upgrade internal name")
i_name = input().strip()
print("Enter the title for the upgrade")
title = input().strip()

print("Now write the full description.")
print("You can use @1, @2, ... as placeholders for variables.")
print("Use a new line for each line of text.")
print("When you are done, enter '$$$' on a new line.")

desc_lines = []
while True:
    temp = input()
    if temp == "$$$":
        break
    desc_lines.append(temp)

# Join multiple lines with \n so they can be split later by the compiler
desc_text = "\n".join(desc_lines)

# Ensure the level exists in the dict
if str(level) not in data:
    data[str(level)] = {}

# Insert/overwrite this upgrade
data[str(level)][str(i_name)] = {
    "title": title,
    "description": desc_text
}

print("Your description looks like this:")
print(json.dumps(data, indent=4))

# Save back
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)
