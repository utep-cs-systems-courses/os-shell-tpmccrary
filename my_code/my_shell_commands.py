import os, sys, re

# Given arguments, change the current working directory.
def changeDirectory(inputArgs):
    try:
        os.chdir(inputArgs[1])
    except FileNotFoundError:
        os.write(1, ("bash: cd: No such file or directory\n").encode())