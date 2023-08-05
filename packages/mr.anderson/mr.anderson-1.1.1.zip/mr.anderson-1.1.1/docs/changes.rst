Changelog
=========

.. Use the following to start a new version entry:

   |version| (unreleased)
   ----------------------

   - change message [author]

1.1.1 (2011-10-27)
------------------

- Moved the templates from the static directory to a templates directory.
  [pumazi]
- Fixed PloneConfig to handle None values for the plone version, extends and
  distributions. [pumazi]

1.1 (2011-10-26)
----------------

- Configure the Plone 4.x.cfg to use ``${buildout:eggs}`` rather than
  ``${instance:eggs}`` so that ``bin/test`` can be called without additional
  options. [pumazi]
- Added configuration of Plone 3.x. [pumazi]

1.0 (2011-10-25)
----------------

- Using the multi-line configuration value indent style rather than one
  line with multiple values. [pumazi]

1.0b1 (2011-10-21)
------------------

- Write the ``bootstrap.py`` script to the build directory. [pumazi]
- Write out the ``base.cfg`` with the specified Plone version. [pumazi]
- Generalize the Plone major version configuration into a single template
  file. [pumazi]
- Added the ``--latest`` option to use the latest of whatever major/minor
  Plone version. [pumazi] 
- Added the ``--extend-with`` option to allow for additional configuration
  (e.g. sources.cfg, good-py, versions.cfg, etc.). [pumazi]
- Added the ``--distributions`` option to allow for the addition of eggs
  (a.k.a. Python distributions). [pumazi]

1.0a1 (2011-10-21)
------------------

- Initial release. [pumazi]
