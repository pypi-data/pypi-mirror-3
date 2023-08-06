import pyxb.binding.generate
import pyxb.utils.domutils

import os.path
schema_path = '%s/../schemas/test-include-ddq.xsd' % (os.path.dirname(__file__),)
code = pyxb.binding.generate.GeneratePython(schema_location=schema_path)
#file('code.py', 'w').write(code)
rv = compile(code, 'test', 'exec')
eval(rv)

from pyxb.exceptions_ import *

import unittest

class TestIncludeDD (unittest.TestCase):
    def testDefault (self):
        xmls = '<entry xmlns="%s"><from>one</from><to>single</to></entry>' % (Namespace.uri(),)
        instance = CreateFromDocument(xmls.encode('utf-8'))
        self.assertEqual(english.one, instance.from_)

    def testExplicit (self):
        xmls = '<ns:entry xmlns:ns="%s"><ns:from>one</ns:from><ns:to>single</ns:to></ns:entry>' % (Namespace.uri(),)
        instance = CreateFromDocument(xmls.encode('utf-8'))
        self.assertEqual(english.one, instance.from_)

if __name__ == '__main__':
    unittest.main()
    
