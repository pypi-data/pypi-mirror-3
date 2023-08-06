#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of the wempy template system
Copyrighted by G. Clifford Williams <gcw@notadiscussion.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

Author: G. Clifford Williams (for wempy templating system) 

Contributors:

- Thank you to Thadeus Burgess for the re-write of gluon/template.py
- Thank you to Massimo Di Pierro for creating the original gluon/template.py
- Thank you to Jonathan Lundell for extensively testing the regex on Jython.
- Thank you to Limodou (creater of uliweb) who inspired the block-element support for web2py.
"""

import os, getopt, sys, fileinput, cStringIO
import wemplate


def usage():
    usage_message = """
usage: 
%s [options] [intputfiles] 
    -x print python script
    -p template path (where to look for templates with relative paths)

""" % (sys.argv[0])
    print(usage_message)

def get_file_text(filename):
    if isinstance(filename, str):
        try:
            fp = open(os.path.join(path, filename), 'rb')
            text = fp.read()
            fp.close()
        except IOError:
            raise RestrictedError(filename, '', 'Unable to find the file')
    else:
        text = filename.read()
    return text

def process(filein=False, bitsin=False, parsed=False):
    if filein:
        bitsin = get_file_text(filein)
    if not filein and not bitsin:
        bitsin = sys.stdin.read()
    parser = wemplate.TemplateParser(bitsin,path=path)
                                
    return str(parser) if parsed else parser.render()
    

def start():
    """
    This function simply 
    """
    want_parsed = False
    try:
        opciones, input_files = getopt.getopt(sys.argv[1:], "p:hx?",
                                        ["help", "version"])
    except getopt.GetoptError, err:
        print str(err) #print out the value of the error
        usage()
        sys.exit(2)
    for o, a in opciones: #process the options supplied on the command line
        if o == "-p":
            global path
            path = os.path.abspath(a)
        elif o == "-x":
            want_parsed = True
        elif o in ("-?", "-h", "--help"):
            usage()
            sys.exit()

    if len(input_files) > 0: #process files specified on the command line
        for file_name in input_files:
            sys.stdout.write(process(file_name, parsed=want_parsed))
    else:
        sys.stdout.write(process(bitsin=sys.stdin.read(), parsed=want_parsed))
        
global path 
path = os.getcwd()

if __name__ == "__main__" :
    start()
