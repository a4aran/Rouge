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
level = input()
print("Enter the upgrade internal name")
i_name = input()
print("Enter the title for the upgrade")
title = input()
print("Description writing starts now")
print("You'll first write the half before the stats")
print("In order to end this part of writing you'll need to enter '$$$'")

desc_part_1 = []
while True:
    temp = input()
    if temp == "$$$":
        break
    desc_part_1.append(temp)

print("Now write the half after the stats (end with $$$)")
desc_part_2 = []
while True:
    temp = input()
    if temp == "$$$":
        break
    desc_part_2.append(temp)

# Ensure the level exists in the dict
if str(level) not in data:
    data[str(level)] = {}

# Insert/overwrite this upgrade
data[str(level)][str(i_name)] = {
    "title": str(title),
    "description": [
        desc_part_1,
        desc_part_2
    ]
}

print("Your description looks like this:")
print(json.dumps(data, indent=4))

# Save back
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)
