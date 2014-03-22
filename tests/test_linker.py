#!/usr/bin/env python
from os import path
from shutil import copytree, rmtree
from socket import gethostname
from unittest import main, TestCase

from linker import Linker

class FunctionalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = path.join(path.dirname(__file__), 'test_path')
        copytree(path.join(cls.root, 'hostname'),
                 path.join(cls.root, gethostname()))

    @classmethod
    def tearDownClass(cls):
        rmtree(path.join(cls.root, gethostname()))

    # TODO finish tests

    def test_fetch_file_list(self):
        linker = Linker()
        want_output = ['commonfile1', '_tmp_commonfile4', 'commonfile5']
        have_output = linker.fetch_file_list(path.join(self.root, 'common'))

        want_output.sort()
        have_output.sort()
        self.assertListEqual(want_output, have_output)

    def test_fine_files(self):
        linker = Linker()
        want_output = ['commonfile1', '_tmp_commonfile4', 'commonfile5',
                       'hostname_file1']
        have_output = linker.find_files(self.root)

        want_output.sort()
        have_output.sort()
        self.assertListEqual(want_output, have_output)

if __name__ == '__main__':
    main()
