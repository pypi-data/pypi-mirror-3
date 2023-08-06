
#import os
from optparse import OptionParser

##############################################################################
# Functions
##############################################################################

def hello():
    parser = OptionParser(usage="usage: %prog <name>")    
    options, args = parser.parse_args()
    if not args:
        parser.error("You must specify a name")
    name = args[0]
    if type(name) == str:
        name = name.decode('utf-8')
    print("Hello "+name)

