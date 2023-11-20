#!/bin/python

import sys

if len(sys.argv) < 2:
    print("USAGE: <script.py> <input.bin>")
    exit(0)
out_str = ''
bytes = None 

with open(sys.argv[1], 'rb') as file:
    bytes = file.read()

for idx in range(0, len(bytes)-200):
    if bytes[idx] == 0x10:
        i = idx
        for i in range(idx+189, idx+253):
            if bytes[i] != 0:
                break 
        if i == (idx+252) and bytes[i+1] != 0:
            out_str += 'offset ' + hex(idx)
            out_str += ", AmbiqSuite SDK Apollo image, RAM address 0x10000000,"
            out_str += 'Vector Table start from ' + hex(idx-2) + ','
            if bytes[idx+3] == 0x10:
                out_str += 'Base Address 0x18000'
            elif bytes[idx+3] == 0x0:
                out_str += 'Base Address 0xc000'
            else:
                out_str += 'Unknown Base Address'
            out_str += '\n'

print(out_str)
