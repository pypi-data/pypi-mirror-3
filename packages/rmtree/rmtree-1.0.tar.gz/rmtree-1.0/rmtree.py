#!/usr/bin/env python

from os import path
from shutil import rmtree
import argparse

HOME=path.expanduser("~")

def parse_path(path):
    path=list(path)
    if path[0] == "~":
        path[0] = HOME
    return ''.join(path)

#_________________________________________________________________________________________
#                   Parse Args

def parse_args():

    parser = argparse.ArgumentParser(
        prog="rmtree",
        description="Purpose: A command line tool to remove a tree using python's shutil.rmtree",
        epilog="rmtree developed by Luis Naranjo <luisnaranjo733@hotmail.com>"
    )
    parser.add_argument('tree',help="Path to removal tree.")
    args = parser.parse_args()
    return args.tree
#_________________________________________________________________________________________
#                   Wrapper

def main():
    args=parse_args()
    tree = parse_path(args)
    try:
        rmtree(tree)
    except OSError:
        print "ERROR - Does '%s' exist?" % args

if __name__ == "__main__":
    main()
