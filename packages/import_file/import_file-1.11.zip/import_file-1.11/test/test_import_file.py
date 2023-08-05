# -*- coding: utf-8 -*-

import unittest
import os
import shutil

from import_file import import_file

os.chdir(os.path.dirname(__file__) or '.')

MAGIC_VAR_EXPECTED = 123

STUB_NAME = 'stub.py'
STUB_DIR = 'tools'
STUB_LOC = os.path.join(STUB_DIR, STUB_NAME)

#UNICODE_DIR = 'עברית' # this works in python 3, but not in python 2
UNICODE_DIR = b'\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa'.decode('utf-8')
STUB_LOC = os.path.join(STUB_DIR, STUB_NAME)
STUB_UNICODE_LOC = os.path.join(STUB_DIR, UNICODE_DIR, STUB_NAME)
#STUB_UNICODE_DIR_AND_FNAME = 'tools\\עברית\\א.py'
STUB_UNICODE_DIR_AND_FNAME = b'tools\\\xd7\xa2\xd7\x91\xd7\xa8\xd7\x99\xd7\xaa\\\xd7\x90.py'.decode('utf-8')


class TestCase(unittest.TestCase):
    def testImportsHere(self):
        shutil.copy(STUB_LOC, '.')
        try:
            stub = import_file(STUB_NAME)
            self.assertEqual(stub.A_VAR, MAGIC_VAR_EXPECTED)
        finally:
            os.remove(STUB_NAME)

    def testRelativeImport(self):
        to_import = STUB_LOC
        stub = import_file(to_import)
        self.assertEqual(stub.A_VAR, MAGIC_VAR_EXPECTED)

    def testAbsoluteImport(self):
        to_import = os.path.abspath(STUB_LOC)
        stub = import_file(to_import)
        self.assertEqual(stub.A_VAR, MAGIC_VAR_EXPECTED)
        
    def testPackageImport(self):
        stub_package = import_file('stub_package')
        self.assertEqual(stub_package.A_VAR, MAGIC_VAR_EXPECTED)

    def testFails(self):
        self.assertRaises(ImportError, import_file, 'whatever_doesnt_exist')
        self.assertRaises(ImportError, import_file, 'whatever_doesnt_exist.py')

    def testRelativeUnicodePath(self):
        os.chdir(os.path.join(STUB_DIR, UNICODE_DIR))
        stub = import_file(STUB_NAME)
        self.assertEqual(stub.A_VAR, MAGIC_VAR_EXPECTED)
    
    # I'm not sure if and how to support this feature
    #def testRelativeUnicodePathAndFilename(self):
    #    stub = import_file(STUB_UNICODE_DIR_AND_FNAME)
    #    self.assertEqual(stub.A_VAR, MAGIC_VAR_EXPECTED)

if __name__ == '__main__':
    unittest.main()

