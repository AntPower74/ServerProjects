import re

lines = [
    "TORINO - Autostazione c.so Bolzan0o8 .:.1...9.................................................................................................................................................",
    "Torino - Deposito ...........................0..8...:.4...9..................................................................................................................",
    "To - lungo dora firenze ........................0..4...:.2...1....................................................................................................................."
]

for line in lines:
    # Remove all the dots at the end
    line = re.sub(r'\.+$', '', line).strip()
    
    # Extract the name and the messy time part
    # Look for the last occurrence of digits and colons (with dots/spaces)
    m = re.search(r'^(.*?)([\d\.\s:]+)$', line)
    if m:
        name = m.group(1).strip()
        time_raw = m.group(2)
        # clean the time
        time_clean = re.sub(r'[^\d:]', '', time_raw)
        # clean the name by removing lingering dots and digits at the end if they bleed into it
        # Actually "Bolzan0o8" is bleeding digits into name!
        # Wait, the time is always 4 digits and 1 colon: \d\d:\d\d
        print(f"Name: {name} | TimeRaw: {time_raw} | TimeClean: {time_clean}")

