#! /usr/bin/env python

from distutils.core import setup
import sys, subprocess, os


RELEASE = 1

with file('VERSION', 'rt') as f:
    version = f.read().strip()

if os.path.isdir('.hg'):
    # Check if the VERSION file should be modified:
    revision = subprocess.check_output(['hg', 'parents', '--template', '{node}']).strip()
    newversion = '%d.%s' % (RELEASE, revision)

    # If there are any modified or unexpected files, the version has '-dev' appended:
    details = subprocess.check_output(['hg', 'status']).strip()
    if len(details) > 0:
        newversion += '-dev'
        sys.stderr.write('Appending "-dev" to version because of:\n%s\n' % (details,))

    if version != newversion:
        sys.stderr.write('Updating VERSION from %r to %r\n' % (version, newversion))
        version = newversion
        with file('VERSION', 'wt') as f:
            f.write(version)

setup(name = 'concon',
      description = 'CONstrained CONtainers: immutable and append-only container subclasses and utilities.',
      url = 'https://bitbucket.org/nejucomo/concon',
      license = 'MIT (see LICENSE.txt)',
      version = version,
      author = 'Nathan Wilcox',
      author_email = 'nejucomo@gmail.com',
      py_modules = ['concon', 'test_concon'],
      )
