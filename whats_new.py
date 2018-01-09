#!/usr/bin/env python3

"""Script for generating a what's file in ./clid/"""

with open('CHANGELOG.md', 'r') as log:
    lines = log.readlines()
    new = lines[lines.index('\n') + 1: lines.index('- - -\n')]

temp = []
for line in new:
    if line.startswith('- '):
        temp.append('- ' + line[6:])
    else:
        temp.append(line)

with open('clid/NEW.txt', 'w') as file:
    file.writelines(temp)
