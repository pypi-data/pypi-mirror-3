# -*- coding: utf-8 -*-
from mr.anderson.testing import unittest
import os
import tempfile
import shutil


class PlongConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    def make_one(self, *args, **kwargs):
        from mr.anderson.builder import PloneConfig
        config = PloneConfig(*args, **kwargs)
        return config

    def test_config_not_found(self):
        version = "2.5"
        # Make a configuration
        config = self.make_one(version)

        # Verify write raises an error when the versioned config can't
        # be found.
        from mr.anderson.builder import ConfigNotFound
        with self.assertRaises(ConfigNotFound):
            config.write(self.tmpdir)

    def test_find_config(self):
        version = "4.1.1"
        # Make a configuration
        config = self.make_one(version)
        config.write(self.tmpdir)

        # Verify the config writes out as expected
        cfg = open(os.path.join(self.tmpdir, 'buildout.cfg'), 'r').read()
        # Meh, this will work for now, but there are better ways of finding this stuff
        extends_line = [line for line in cfg.split('\n') if line.find('extends') == 0][0]
        extends = [e.strip() for e in extends_line.split('=')[-1].split()]
        self.assertIn('base.cfg', extends)

    def test_extends(self):
        version = "4.1.1"
        test_extends = ('sources.cfg', 'goodpy.cfg',)
        # Make a configuration
        config = self.make_one(version, extends=test_extends)
        config.write(self.tmpdir)

        # Verify the config writes out as expected
        cfg = open(os.path.join(self.tmpdir, 'buildout.cfg'), 'r').read()
        # Meh, this will work for now, but there are better ways of finding this stuff
        extends_line = [line for line in cfg.split('\n') if line.find('extends') == 0][0]
        extends = [e.strip() for e in extends_line.split('=')[-1].split()]
        for e in test_extends:
            self.assertIn(e, extends)
        self.assertEqual('base.cfg', extends[0])

    def test_distributions(self):
        version = "4.1.1"
        test_dists = ['one', 'two >=3', 'fish [red,blue]']
        # Make a configuration
        config = self.make_one(version, distributions=test_dists)
        config.write(self.tmpdir)

        # Now squeeze up the distribution names so that buildout doesn't
        # choke on them.
        test_dists = [i.replace(' ', '') for i in test_dists]

        # Verify the config writes out as expected
        cfg = open(os.path.join(self.tmpdir, 'buildout.cfg'), 'r').read()
        dist_line = [line for line in cfg.split('\n') if line.find('eggs') == 0][0]
        dists = [d.strip() for d in dist_line.split('+=')[-1].split()]
        for d in test_dists:
            self.assertIn(d, dists)

    def test_base_files_exist(self):
        version = "4.1.1"
        # Make a configuration
        config = self.make_one(version)
        config.write(self.tmpdir)

        # Verify the config writes out as expected
        bootstrap_py = os.path.join(self.tmpdir, 'bootstrap.py')
        base_cfg = os.path.join(self.tmpdir, 'base.cfg')
        self.assertTrue(os.path.exists(bootstrap_py), "couldn't find bootstrap.py")
        self.assertTrue(os.path.exists(base_cfg), "couldn't find base.cfg")

    def test_latest(self):
        version = "4.1.1"
        # Make a configuration
        config = self.make_one(version)
        config.write(self.tmpdir)

        # Verify the version is correct in the base.cfg and that it is
        # exactly as specified.
        base_cfg = os.path.join(self.tmpdir, 'base.cfg')
        with open(base_cfg, 'r') as f:
            # Grab the 3rd line, because We know that will have the version on it
            for i in range(0,3):
                line = f.readline()
        self.assertTrue(line.find(version) >= 0, "version wasn't found")

        # And again with latest
        config = self.make_one(version, use_latest=True)
        config.write(self.tmpdir)

        # Check for the latest version specifier
        with open(base_cfg, 'r') as f:
            # Grab the 3rd line, because We know that will have the version on it
            for i in range(0,3):
                line = f.readline()
        self.assertTrue(line.find('4.1-latest') >= 0, "version wasn't found")

        # And once more without the minor version
        version = '4'
        config = self.make_one(version, use_latest=True)
        config.write(self.tmpdir)

        # Check for the latest version specifier
        with open(base_cfg, 'r') as f:
            # Grab the 3rd line, because We know that will have the version on it
            for i in range(0,3):
                line = f.readline()
        self.assertTrue(line.find('4-latest') >= 0, "version wasn't found")
