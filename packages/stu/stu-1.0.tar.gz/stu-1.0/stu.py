#!/usr/bin/env python


import os
from sys import exit
import argparse
from getpass import getuser
from time import strftime

class Creator(object):
    def __init__(self):
        self.args = self.get_args()
        
        self.args['time'] = strftime("%x")
        self.args['year'] = strftime("%Y")

        if self.args['interactive']:
            self.interactive_mode()
        self.string = self.make_string()
        
       # if self.interactive:
          #  self.interactive_mode            
        
    def interactive_mode(self):
        if not self.args['purpose']:
            self.args['purpose'] = raw_input("Purpose  :\t")
        if not self.args['license']:
            self.args['license'] = raw_input("License  :\t")
        if not self.args['version']:
            self.args['version'] = raw_input("Version  :\t")

        
    def get_args(self):
        parser = argparse.ArgumentParser(
            description="Purpose: A basic template for python scripts\nNote: You must be in the same directory as the destination file.",
            epilog="Developed by Luis Naranjo.\n"
        )
        
        parser.add_argument(
        '-i','--interactive',
        help="Query the user for all script specifications.",
        action='store_true',
        dest='interactive',
        )
        
        parser.add_argument(
        'name',
        help="Specify the name of the destination script.",
        )

        parser.add_argument(
        '-p', '--purpose',
        help="Specify the purpose of the destination script.",
        dest="purpose",
        )
        
        parser.add_argument(
        '-l', '--license',
        help="Specify the type of license of the destination script.",
        dest="license",
        )

        parser.add_argument(
        '-v', '--version',
        help="Specify the version number of the destination script.",
        dest='version'
        )
        
        parser.add_argument(
        '-a', '--author',
        help="Specify the author of the destination script.",
        default=getuser(),
        dest='author',
        
        
        )
        
        args = parser.parse_args()
        
        argv = {
            'name': args.name,
            'purpose': args.purpose,
            'license': args.license,
            'version': args.version,
            'interactive': args.interactive,
            'author': args.author,
        }
        return argv





    def make_string(self):
        args = self.args
        version = args['version']
        if version:
            version = "-" + version
        if not version:
            version =''
        
        txt = """
#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Name:        %s%s
# Purpose:     %s
#
# Author:      %s
#
# Created:     %s
# Copyright:   (c) %s %s
# License:     %s
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    pass
""" % (args['name'], version, args['purpose'], args['author'], args['time'], args['author'], args['year'], args['license'])
        return txt


    def writer(self):
        path = self.args['name']
        #if 'y' != list(path)[-1] and '.' != list(path)[-3]: #Adds .py to files that don't have it, for convenience.
            #path = path + ".py"
            
        is_file = os.path.isfile(path)
        
        if is_file:
            raise Exception, "%s already exists!" % path
            
        if not is_file:
            txt = open(path, 'w')
            txt.write(self.string)
            txt.close()

def main():
    create = Creator()
    create.writer()
    
if __name__ == "__main__":
    main()
    
