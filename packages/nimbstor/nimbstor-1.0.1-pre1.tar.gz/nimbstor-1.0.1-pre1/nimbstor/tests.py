import unittest
import doctest
import nimbstor.stor
import nimbstor.tar

test_all = unittest.TestSuite()
test_all.addTest(doctest.DocTestSuite(nimbstor.stor))
test_all.addTest(doctest.DocTestSuite(nimbstor.tar, optionflags = doctest.ELLIPSIS))
