
#! /usr/bin/env python3
#
# readlines.py.  Demo of buffered stdin semantics
#

from my_read import myReadLine

from sys import stdin, stdout

numLines = 0

inLine = myReadLine()
print(f"Stdin uses file descriptor {stdin.fileno()}\n")
print(f"Stdout uses file descriptor {stdout.fileno()}\n")
while len(inLine):
    numLines += 1
    stdout.write(f"### Line {numLines}: <{str(inLine)}> ###\n")
    inLine = myReadLine()
stdout.write(f"EOF after {numLines} lines\n")