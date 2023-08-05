# -*- coding: utf-8 -*-

import doctest
import unittest

import zc.buildout.tests
import zc.buildout.testing

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('plone.recipe.haproxy', test)


def test_suite():
    suite = unittest.TestSuite((
        doctest.DocFileSuite(
            'download.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=optionflags,
            ),
        ))
    return suite
