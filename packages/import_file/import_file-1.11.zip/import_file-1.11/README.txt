import_file

import_file is meant to import a python script from far a normal file path.
Relative (dotted) imports are complicated, and fixing sys.path just feels wrong.

Usage examples:
>>>from import_file import import_file
>>>mylib = import_file('c:\\mylib.py')
>>>another = import_file('relative_subdir/another.py')

So now you aren't limited to importing only within your package or trail of
__init__.py files.

This should work for python 2.5-3.2 and it's public domain, have fun.


ubershmekel at gmail
http://uberpython.wordpress.com

