#! /usr/bin/env python

"""
Python tool for testing the use of `exec` in EmPy compound statements, @{...}

Original Author: David Banas
Original Date:   July 28, 2012

Copyright (c) 2012 David Banas; All rights reserved World wide.
"""

import em

def main():
    interpreter = em.Interpreter()
    try:
        interpreter.file(open('empy_exec_test.em'))
    finally:
        interpreter.shutdown()

if __name__ == '__main__':
    main()

