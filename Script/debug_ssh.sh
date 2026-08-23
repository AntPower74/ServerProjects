#!/bin/bash
echo "=== /home/cup perms ===" 
ls -ld /home/cup
echo "=== .ssh perms ==="
ls -la /home/cup/.ssh/
echo "=== authorized_keys content ==="
cat /home/cup/.ssh/authorized_keys
echo "=== sshd log test ==="
sshd -T 2>/dev/null | grep -i "authorizedkeys\|strictmodes\|pubkey"
