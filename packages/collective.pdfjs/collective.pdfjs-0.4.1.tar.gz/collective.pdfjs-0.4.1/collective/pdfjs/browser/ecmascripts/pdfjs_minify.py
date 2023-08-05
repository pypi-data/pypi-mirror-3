#!/usr/bin/env python
"""
A dedicated minificator for pdf.js
"""
import sys
import re

SAFE_SYMBOLS = ';:='

def strip_symbols(data, symbols):
    for sym in symbols:
        data = re.sub(''.join((' ', sym, ' ')), sym, data)
        data = re.sub(''.join((sym, ' ')), sym, data)
        data = re.sub(''.join((' ', sym)), sym, data)
    return data

def strip_comments(data):
    # Strip all comments
    data = re.sub(
    '(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|(//.*)', '', data,
    )
    return data

def minify(data, level=1):
    # Level 1
    if level < 2:
        data = strip_comments(data)
        data = re.sub(' +', ' ', data)
        data = re.sub('\\t', '', data)
        #data = re.sub('\\n', '', data)
        data = strip_symbols(data, SAFE_SYMBOLS)
    return data

class Minificator(object):

    def __init__(self):
        self.data = None

    def read(self, file_path):
        """
        Read and store the text
        """
        path = file_path
        try:
            with open(path, 'r') as fd:
                self.data = fd.read()
        except IOError, e:
            print "Error: could not open file \'%s\': %s" % (path, e)

    @property
    def has_data(self):
        return True if self.data else False

    def write(self):
        print minify(self.data)


def usage():
    return """%s - a dedicated minificator for pdf.js

Usage:
    ./%s pdf.js > pdf.min.js
    """ % tuple(2*[sys.argv[0]])

def main():
    try:
        path = sys.argv[1]
    except IndexError:
        print usage()
        sys.exit(0)

    mini = Minificator()
    mini.read(path)
    if mini.has_data:
        mini.write()
    sys.exit(1)


if __name__ == '__main__':
    main()
