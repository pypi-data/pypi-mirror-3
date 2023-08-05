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
        version = "2.5.x"
        # Make a configuration
        config = self.make_one(version)

        # Verify write raises an error when the versioned config can't
        # be found.
        from mr.anderson.builder import ConfigNotFound
        with self.assertRaises(ConfigNotFound):
            config.write(self.tmpdir)

    def test_find_config(self):
        version = "4.1.x"
        # Make a configuration
        config = self.make_one(version)

        # Verify the config writes out as expected
        config.write(self.tmpdir)
        cfg = open(os.path.join(self.tmpdir, 'buildout.cfg'), 'r').read()
        # Meh, this will work for now, but there are better ways of finding this stuff
        extends_line = [line for line in cfg.split('\n') if line.find('extends') == 0][0]
        self.assertTrue(extends_line.find("%s.cfg" % version) >= 0, "couldn't find versioned cfg")
