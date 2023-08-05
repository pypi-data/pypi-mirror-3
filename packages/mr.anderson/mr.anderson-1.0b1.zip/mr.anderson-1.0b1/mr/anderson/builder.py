# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import shutil

from pkg_resources import parse_version

logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))
here = os.path.abspath(os.path.dirname(__file__))
STATIC = os.path.join(here, 'static')

BUILDOUT_CFG = """\
[buildout]
extends = %(extends)s
eggs += %(distributions)s
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
    new_version = []
    for i, part in enumerate(version_parts):
        # Only go as far as the minor version to finalized bit.
        if part.startswith('*') or i >= 2:
            break
        new_version.append(str(int(part)))
    new_version = '.'.join(new_version)
    new_version += suffix
    return new_version

def find_config(version, base_dir=STATIC):
    """Find a configuration file with the given name and return its
    absolute path."""
    major_version = int(parse_version(version)[0])
    named_cfg = "%s.x.cfg" % major_version
    path = os.path.join(base_dir, named_cfg)
    if not os.path.exists(path):
        raise ConfigNotFound(base_dir, named_cfg)
    return path


class PloneConfig(object):
    """Plone configuration class"""

    def __init__(self, version, use_latest=False, extends=[], distributions=[]):
        self.version = version
        self.use_latest = use_latest
        if not hasattr(extends, '__iter__'):
            extends = [extends]
        self.extends = list(extends)
        if not hasattr(distributions, '__iter__'):
            distributions = [distributions]
        # Remove misc spaces from the names, because buildout will
        # split on the spaces
        distributions = [d.replace(' ', '') for d in distributions]
        self.distributions = distributions

    def _copyfile(self, src, dest):
        """Wrapper on shutil.copyfile"""
        basename = os.path.basename(src)
        if os.path.exists(dest):
            state = False
        else:
            shutil.copyfile(src, dest)
            state = True
        return state

    def write(self, dir):
        """Write out the configuration to the specified directory."""
        logger.info("Writing configuration to:\n   %s" % dir)

        # Write bootstrap.py
        filename = 'bootstrap.py'
        bootstrap_py = os.path.join(STATIC, filename)
        dest = os.path.join(dir, filename)
        was_copied = self._copyfile(bootstrap_py, dest)
        if was_copied:
            logger.info("Wrote %s" % filename)
        else:
            logger.info("%s exists, not writing" % filename)

        # Write base.cfg
        cfg_template = open(find_config(self.version), 'r').read()
        filename = 'base.cfg'
        version = self.version
        if self.use_latest:
            version = convert_to_minor_version(self.version)
            version = "%s-latest" % version
        logger.info("Using Plone version %s" % version)
        cfg = cfg_template % dict(version=version)
        # Always write the base.cfg, even if it exists
        base_cfg = os.path.join(dir, filename)
        with open(base_cfg, 'w') as f:
            f.write(cfg)
        logger.info("Wrote %s" % filename)

        # Assign base.cfg as the first extended configuration
        self.extends.insert(0, 'base.cfg')

        # Write buildout.cfg
        buildout_cfg = os.path.join(dir, 'buildout.cfg')
        extends = ' '.join(self.extends)
        distributions = ' '.join(self.distributions)
        with open(buildout_cfg, 'w') as cfg:
            configuration = BUILDOUT_CFG % dict(extends=extends,
                                                distributions=distributions,
                                                )
            cfg.write(configuration)
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
    parser.add_argument('--verbose', action='store_true')
    # parser.add_argument('-e', '--python-executable',
    #                     help="executable used to build")
    parser.add_argument('-p', '--with-version', nargs='?',
                        default='4')
    parser.add_argument('--latest', action='store_true',
                        help="use the latest release (e.g. 4.1 -> 4.1-latest)")
    parser.add_argument('--extend-with', nargs='*',
                        help="other configuration files to extend")
    parser.add_argument('-d', '--distributions', nargs="*",
                        help="distributions to include in the build")
    parser.add_argument('output_dir', nargs='?',
                        action=DirectoryAction,
                        default=os.path.abspath(os.curdir),
                        help="output directory location")

    args = parser.parse_args()

    # package_name = args.package_name[0]
    # if args.package_source_location is None and package_name is not None:
    #     args.package_source_location = "src/%s" % package_name

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    output_directory = args.output_dir[0]
    # python_executable = args.python_executable
    # if python_executable is None:
    #     logger.warn("You didn't supply a --python-executable. Consider "
    #                 "changing this. sys.executable will be used, but may "
    #                 "not be the intended.")
    #     python_executable = sys.executable

    config = PloneConfig(version=args.with_version,
                         use_latest=args.latest,
                         extends=args.extend_with,
                         distributions=args.distributions,
                         ) 
    config.write(output_directory)
    sys.exit(0)


if __name__ == '__main__':
    main()
