import json
p = "frontend/package.json"
with open(p) as f: d = json.load(f)
d['devDependencies']['tailwindcss'] = "^3.4.17"
d['devDependencies']['postcss'] = "^8.4.31"
d['devDependencies']['autoprefixer'] = "^10.4.16"
with open(p, 'w') as f: json.dump(d, f, indent=2)
print("Downgraded Tailwind in package.json")
