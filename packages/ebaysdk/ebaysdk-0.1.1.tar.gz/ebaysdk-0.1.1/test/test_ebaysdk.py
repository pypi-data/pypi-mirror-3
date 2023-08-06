import unittest
import doctest
import sys
import os

sys.path.append('.')
import ebaysdk

def runtests():
   unittest.main()
   
class Test(unittest.TestCase):
    """Unit tests for ebaysdk."""

    def test_doctests(self):
        """Run ebaysdk doctests"""
        doctest.testmod(ebaysdk)
        #import ebaysdk
        #p = doctest.DocTestParser()
        #p.get_doctest(ebaysdk.html.__doc__, {}, 'foo', 'foo.py', 0)
        #t = p.get_doctest(ebaysdk.html.__doc__, {}, 'foo', 'foo.py', 0)
        #case = doctest.DocTestCase(t)
        #case.runTest()

        #p.get_doctest(ebaysdk.finding.__doc__, {}, 'foo', 'foo.py', 0)
        #t = p.get_doctest(ebaysdk.finding.__doc__, {}, 'foo', 'foo.py', 0)
        #case = doctest.DocTestCase(t)
        #case.runTest()

if __name__ == "__main__":
    unittest.main()


