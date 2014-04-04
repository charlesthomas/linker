#!/usr/bin/env python
from os import listdir, mkdir, path, remove
from shutil import copytree, rmtree
from socket import gethostname
from unittest import main, TestCase

from linker import Linker

class BaseCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indir = path.join(path.dirname(__file__), 'input')
        cls.outdir = path.join(path.dirname(__file__), 'output')
        copytree(path.join(cls.indir, 'hostname'),
                 path.join(cls.indir, gethostname()))

    @classmethod
    def tearDownClass(cls):
        rmtree(path.join(cls.indir, gethostname()))

    def setUp(self):
        mkdir(self.outdir)

    def tearDown(self):
        rmtree(self.outdir)

    def touch(self, dirname, basename=None):
        if basename is None:
            open(path.join(dirname), 'a').close()
        else:
            open(path.join(dirname, basename), 'a').close()

class FunctionalTests(BaseCase):
    def setUp(self):
        super(FunctionalTests, self).setUp()
        self.linker = Linker(self.indir, self.outdir)

    def test_move_first(self):
        test_file = '/tmp/test_file'
        self.touch(self.outdir, test_file)
        self.linker = Linker(self.indir, test_file)
        test_link = path.join(self.indir, gethostname(),
                              self.linker.generate_target(test_file))
        try:
            self.linker.move_to_target()
            self.assertTrue(path.exists(test_file))
            self.assertTrue(path.islink(test_file))
            self.assertTrue(path.exists(test_link))
            self.assertFalse(path.islink(test_link))
            self.assertEqual(path.realpath(test_file), test_link)
        finally:
            remove(test_file)

    def test_move_first_common(self):
        test_file = '/tmp/test_file'
        self.touch(self.outdir, test_file)
        self.linker = Linker(self.indir, test_file)
        test_link = path.join(self.indir, 'common',
                              self.linker.generate_target(test_file))
        try:
            self.linker.move_to_target(common=True)
            self.assertTrue(path.exists(test_file))
            self.assertTrue(path.islink(test_file))
            self.assertTrue(path.exists(test_link))
            self.assertFalse(path.islink(test_link))
            self.assertEqual(path.realpath(test_file), test_link)
        finally:
            remove(test_file)
            remove(test_link)

    def test_fetch_targets(self):
        want_output = [path.join(self.indir, 'common', f) for f in \
                       ['commonfile1', '.commonfile3', '_tmp_commonfile4',
                        'common__file5']]
        have_output = self.linker.fetch_targets(path.join(self.indir, 'common'))

        want_output.sort()
        have_output.sort()
        self.assertListEqual(want_output, have_output)

    def test_find_targets(self):
        want_output = [path.join(self.indir, 'common', f) for f in \
                       ['commonfile1', '.commonfile3', '_tmp_commonfile4',
                        'common__file5']]
        want_output.append(path.join(self.indir, gethostname(),
                           'hostnamefile1'))
        have_output = self.linker.find_targets(self.indir)

        want_output.sort()
        have_output.sort()
        self.assertEqual(want_output, have_output)

    def test_mkdir_p(self):
        want_dir = path.join(self.outdir, 'mkdirp', 'test')
        self.linker.mkdir_p(want_dir)
        self.assertTrue(path.exists(want_dir))
        self.assertTrue(path.isdir(want_dir))

class FullTests(BaseCase):
    def tearDown(self):
        super(FullTests, self).tearDown()
        extraneous_file = '/tmp/commonfile4'
        if path.exists(extraneous_file):
            remove(extraneous_file)

    def test_vanilla(self):
        linker = Linker(target=self.indir, destination=self.outdir)
        want = ['commonfile1', '.commonfile3', 'common_file5', 'hostnamefile1',
                '/tmp/commonfile4']
        linker.make_links()
        have = listdir(self.outdir)
        if path.exists(want[-1]): have.append(want[-1])
        want.sort()
        have.sort()
        self.assertEqual(want, have)

    def test_exclude_common(self):
        linker = Linker(target=self.indir, destination=self.outdir,
                        exclude_common=True)
        want = ['hostnamefile1']
        linker.make_links()
        have = listdir(self.outdir)
        self.assertEqual(want, have)

    def test_dry_run(self):
        linker = Linker(self.indir, self.outdir, dry_run=True)
        want = []
        linker.make_links()
        have = listdir(self.outdir)
        self.assertEqual(want, have)

    def test_move_existing(self):
        want = ['commonfile1', '.commonfile3', 'common_file5', 'hostnamefile1',
                'common_file5.back']
        self.touch(self.outdir, 'common_file5')
        linker = Linker(self.indir, self.outdir)
        linker.make_links()
        have = listdir(self.outdir)
        want.sort()
        have.sort()
        self.assertEqual(want, have)

    def test_delete_existing(self):
        want = ['commonfile1', '.commonfile3', 'common_file5', 'hostnamefile1']
        self.touch(self.outdir, 'common_file5')
        self.assertTrue(not path.islink(path.join(self.outdir, 'common_file5')))
        linker = Linker(self.indir, self.outdir, delete_existing=True)
        linker.make_links()
        have = listdir(self.outdir)
        want.sort()
        have.sort()
        self.assertEqual(want, have)
        self.assertTrue(path.islink(path.join(self.outdir, 'common_file5')))

    def test_common_and_host_file_collision(self):
        '''
        What happens if a file with the same name exists in the common dir and
        in the "hostname" dir?
        Desired behavior is that common is linked first and hostname overwrites
        it, so that common can have a config that applies to all machines, but
        it gets overwritten on a machine by machine basis.
        '''
        real_bothfile = path.join(self.indir, gethostname(), 'bothfile')
        real_bothfile_back = path.join(self.indir, 'common', 'bothfile')
        self.touch(real_bothfile)
        self.touch(real_bothfile_back)
        linker = Linker(self.indir, self.outdir)
        linker.make_links()
        bothfile=path.join(self.outdir, 'bothfile')
        bothfile_back=path.join(self.outdir, 'bothfile.back')
        try:
            self.assertTrue(path.exists(bothfile))
            self.assertTrue(path.exists(bothfile_back))
            self.assertTrue(path.islink(bothfile))
            self.assertTrue(path.islink(bothfile_back))
            self.assertEqual(real_bothfile, path.realpath(bothfile))
            self.assertEqual(real_bothfile_back, path.realpath(bothfile_back))
        finally:
            remove(real_bothfile)
            remove(real_bothfile_back)

    def test_relative_paths(self):
        linker = Linker(target='./tests/input', destination='./tests/output')
        want = ['commonfile1', '.commonfile3', 'common_file5', 'hostnamefile1',
                '/tmp/commonfile4']
        linker.make_links()
        have = listdir(path.abspath(path.expanduser('./tests/output')))
        if path.exists(want[-1]): have.append(want[-1])
        want.sort()
        have.sort()
        self.assertEqual(want, have)

if __name__ == '__main__':
    main()
