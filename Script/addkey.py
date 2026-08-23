#!/usr/bin/env python3
# Add the Penguin key to cup's authorized_keys
key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIpm1/vnZ9BUuiumUqBO43ImaBK+ux1UuaAcklbxczDE antonypotenza@penguin\n"

with open('/home/cup/.ssh/authorized_keys', 'r') as f:
    existing = f.read()

if key.strip() not in existing:
    with open('/home/cup/.ssh/authorized_keys', 'a') as f:
        f.write(key)
    print("Key added.")
else:
    print("Key already present.")
