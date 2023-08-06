
import os
from optparse import OptionParser

##############################################################################
# Functions
##############################################################################

def instantiate_template(template, header, name):
    return template%locals()         

def create_doku_page():
    parser = OptionParser(usage="usage: %prog <filename> <header> <author>")    
    options, args = parser.parse_args()
    if not len(args) == 3:
        parser.error("You must specify a header and author name")
    filename = args[0]
    header = args[1]
    name = args[2]
    if type(header) == str:
        header = header.decode('utf-8')
    if type(name) == str:
        name = name.decode('utf-8')

    template_pathname = os.path.join(os.path.dirname(__file__),'templates','doku.txt')
    f = open(template_pathname, 'r')                                                        
    try:
        template = f.read()                                                            
    finally:                                                                    
        f.close()
    contents = instantiate_template(template, header, name) 
    try:
        p = os.path.abspath(filename)
        f = open(p, 'w')
        f.write(contents.encode('utf-8'))
        print "Created doku page", p
    finally:
        f.close()

