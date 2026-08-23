import re
import urllib.request
import json

url = "https://docs.google.com/spreadsheets/d/1_rr-cS7aGzF5svFS-9mKyq3KnKUbXlkKbGFRwsxd7lI/edit?usp=sharing"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Search for the gridIds and names
matches = re.findall(r'\["([^"]+)",[0-9]+,([0-9]+)\]', html)
if not matches:
    # Google changes their payload structure often, let's try another regex
    matches = re.findall(r'\[\d+,"([^"]+)",(\d+)\]', html)

if not matches:
    matches = re.findall(r'\\",\\"([^"]+)\\"\].*?\[(\d+)\]', html)

print("Found tabs:")
seen = set()
for name, gid in matches:
    if gid not in seen:
        print(f"Name: {name}, GID: {gid}")
        seen.add(gid)
