# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
from subprocess import call

from pkg_resources import parse_version

logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))
here = os.path.abspath(os.path.dirname(__file__))
STATIC = os.path.join(here, 'static')

BUILDOUT_CFG = """\
[buildout]
extends = %(extends)s
"""

class ConfigNotFound(Exception):
    """Raised when a configuration file cannot be found."""


def convert_to_minor_version(version, suffix=''):
    """Given a version, make it look like a minor version
    (e.g. 4.1.2 becomes 4.1). If a suffix is provided, it will be
    added to the end of version.
    """
    # pkg_resouces doesn't have the best versioning library but it will do.
    version_parts = parse_version(version)
    new_version = '.'.join([str(int(p)) for p in version_parts[:2]])
    new_version += suffix
    return new_version

def find_config(name, base_dir=STATIC):
    """Find a configuration file with the given name and return its
    absolute path."""
    named_cfg = "%s.cfg" % name
    path = os.path.join(base_dir, named_cfg)
    if not os.path.exists(path):
        raise ConfigNotFound(base_dir, named_cfg)
    return path


class PloneConfig(object):
    """Plone configuration class"""

    def __init__(self, version):
        self.version = version
        logger.info("Using Plone version %s" % self.version)

    def _set_version(self, v):
        self._version = convert_to_minor_version(v, suffix='.x')
    def _get_version(self):
        return self._version
    version = property(_get_version, _set_version)

    def write(self, dir):
        logger.info("Writing configuration to:\n   %s" % dir)

        base_cfg = find_config(self.version)
        buildout_cfg = os.path.join(dir, 'buildout.cfg')
        with open(buildout_cfg, 'w') as cfg:
            cfg.write(BUILDOUT_CFG % dict(extends=base_cfg))
            logger.info("Wrote buildout.cfg")


class DirectoryAction(argparse.Action):
    """Directory location action"""

    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(values, '__iter__'):
            values = (values,)
        new_values = []
        for value in values:
            path = os.path.abspath(os.path.expanduser(value))
            if not os.path.exists(path):
                raise RuntimeError("Directory not found (%s)" % value)
            new_values.append(path)
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(description="Plone build script")
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    # parser.add_argument('-e', '--python-executable',
    #                     help="executable used to build")
    parser.add_argument('-p', '--with-version', nargs='?',
                        default='4.1.x')
    parser.add_argument('output_dir', nargs='?',
                        action=DirectoryAction,
                        default=os.path.abspath(os.curdir),
                        help="output directory location")
    # parser.add_argument('package_name', nargs=1)

    args = parser.parse_args()

    # package_name = args.package_name[0]
    # if args.package_source_location is None and package_name is not None:
    #     args.package_source_location = "src/%s" % package_name

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    plone_version = args.with_version
    output_directory = args.output_dir[0]
    # python_executable = args.python_executable
    # if python_executable is None:
    #     logger.warn("You didn't supply a --python-executable. Consider "
    #                 "changing this. sys.executable will be used, but may "
    #                 "not be the intended.")
    #     python_executable = sys.executable

    config = PloneConfig(version=plone_version) 
    config.write(output_directory)
    sys.exit(0)


if __name__ == '__main__':
    main()
