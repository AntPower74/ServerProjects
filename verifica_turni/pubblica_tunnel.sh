#!/bin/bash
# Test con ssh localhost.run o pinggy
ssh -o StrictHostKeyChecking=no -R 80:localhost:8085 nokey@localhost.run
