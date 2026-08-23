#!/usr/bin/env python3
import os

src_file = '/home/antonio/.ssh/authorized_keys'
dst_file = '/home/cup/.ssh/authorized_keys'

with open(src_file, 'r') as f:
    src_keys = f.readlines()

dst_keys = []
if os.path.exists(dst_file):
    with open(dst_file, 'r') as f:
        dst_keys = f.readlines()

new_keys = [k for k in src_keys if k not in dst_keys]

if new_keys:
    with open(dst_file, 'a') as f:
        for k in new_keys:
            f.write(k)

os.chmod(dst_file, 0o600)
os.chmod('/home/cup/.ssh', 0o700)
os.chmod('/home/cup', 0o755)
