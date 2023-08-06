"""
util

Utility functions module for cooker
"""
import os
import sys
from fnmatch import fnmatch
from cooker import settings

def message(msg):
    """Display a message to the user if verbose is on."""
    if settings.VERBOSE:
        print msg

def alert(msg='Some error has occured'):
    """Display a message to the user and exit."""
    sys.exit(msg)

def compiler():
    """Compiler options for the a particular language"""
    compilers = {   'c': ["gcc", "main.c"],
                    'cpp': ["g++", "main.cpp"],
                    'java': ["javac", "main.java"],
                    'py': ["true"] # hack for python
                }
    return compilers.get(settings.LANG, ["g++", "main.cpp"])

def binary():
    """Binary file generated"""
    binaries = {   'c': ["./a.out"],
                    'cpp': ["./a.out"],
                    'java': ["java", "main"],
                    'py': ["python", "main.py"]
                }
    return binaries.get(settings.LANG, ["./a.out"])

def guess_language():
    """Guess problem language in current directory"""
    files = os.listdir(os.curdir)
    main = filter(lambda f: fnmatch(f, 'main.*'), files)
    if not len(main):
        alert('Main code file not found.')
    settings.LANG = main[0].split('.')[1]
    if len(main) > 1:
        message('Selecting main.%s from multiple files.' % settings.LANG)
        message('Delete this or override using -l param to check another.')
