import json
import os

target = 'frontend/package.json'
if not os.path.exists(target):
    print("package.json not found")
    exit(1)

with open(target, 'r') as f:
    data = json.load(f)

# Update scripts
data['scripts'] = {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
}

with open(target, 'w') as f:
    json.dump(data, f, indent=2)

print("Updated package.json scripts successfully.")
