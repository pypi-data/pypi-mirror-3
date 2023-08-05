# Copyright (c) 2008-2012 Thomas Lotze
# See also LICENSE.txt

import doctest
import os
import pkg_resources
import unittest
import zc.buildout.testing


flags = (doctest.ELLIPSIS |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)


def setUp(test):
    import virtualenv
    import zc.recipe.egg
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install("virtualenv", test)
    zc.buildout.testing.install("zc.recipe.egg", test)
    zc.buildout.testing.install_develop("tl.buildout_virtual_python", test)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(filename,
                             setUp=setUp,
                             tearDown=zc.buildout.testing.buildoutTearDown,
                             package="tl.buildout_virtual_python",
                             optionflags=flags,
                             )
        for filename in sorted(os.listdir(pkg_resources.resource_filename(
                        'tl.buildout_virtual_python', '')))
        if filename.endswith(".txt")
        ])
