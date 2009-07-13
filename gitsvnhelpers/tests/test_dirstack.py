import os
import unittest
import tempfile
import shutil

from os.path import realpath, join

from jarn.mkrelease.dirstack import DirStack


class DirStackTests(unittest.TestCase):

    def setUp(self):
        # Save cwd
        self.cwd = os.getcwd()
        # Create a dirstack
        self.dirstack = DirStack()
        # Create a sandbox
        self.testdir = realpath(tempfile.mkdtemp())
        os.chdir(self.testdir)
        # Create some dirs
        os.mkdir('foo')
        os.mkdir(join('foo', 'bar'))

    def tearDown(self):
        os.chdir(self.cwd)
        if os.path.isdir(self.testdir):
            shutil.rmtree(self.testdir)

    def testFixture(self):
        self.assertEqual(os.listdir(os.getcwd()), ['foo'])

    def testPushDir(self):
        self.dirstack.push('foo')
        self.assertEqual(self.dirstack.stack, [self.testdir])
        self.assertEqual(os.getcwd(), join(self.testdir, 'foo'))
        self.dirstack.push('bar')
        self.assertEqual(self.dirstack.stack, [self.testdir, join(self.testdir, 'foo')])
        self.assertEqual(os.getcwd(), join(self.testdir, 'foo', 'bar'))

    def testPopDir(self):
        self.dirstack.push('foo')
        self.dirstack.push('bar')
        self.assertEqual(os.getcwd(), join(self.testdir, 'foo', 'bar'))
        self.dirstack.pop()
        self.assertEqual(os.getcwd(), join(self.testdir, 'foo'))
        self.dirstack.pop()
        self.assertEqual(os.getcwd(), self.testdir)
        self.assertEqual(self.dirstack.stack, [])

    def testPushBadDir(self):
        self.assertRaises(OSError, self.dirstack.push, 'peng')

    def testPopEmptyStack(self):
        self.assertEqual(self.dirstack.stack, [])
        self.dirstack.pop()
        self.assertEqual(self.dirstack.stack, [])

    def testStackLen(self):
        self.assertEqual(len(self.dirstack), 0)
        self.dirstack.push('foo')
        self.assertEqual(len(self.dirstack), 1)
        self.dirstack.push('bar')
        self.assertEqual(len(self.dirstack), 2)
        self.dirstack.pop()
        self.assertEqual(len(self.dirstack), 1)
        self.dirstack.pop()
        self.assertEqual(len(self.dirstack), 0)
        self.dirstack.pop()
        self.assertEqual(len(self.dirstack), 0)

