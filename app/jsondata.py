import json

with open('static/data/unemployment.json') as f:
    data = json.load(f)

print(data)
