PURPOSE:
    For creating python scripts with embedded text meta-data.
    Inspired by PyScripter for Windows.

USAGE:
    stu <desired file name> [optional args]
    
    see stu --help for all optional args.
    
REQUIRES:
    argparse

CHANGELOG VERSION 1.1.1:
    1) Made file_name args with .py append .py by default
    2) Under the same above circumstances, gave the file name (title for template) the title without the .py
    3) Fixed a minor bug - can't remember what it was
    
CHANGELOG VERSION 1.1:
    1) Added --overwrite and --name flags
    2) Added functionality for existing files.
    3) Prevented stu from writing to files that have already been stu'd.
    4) Added some comments
