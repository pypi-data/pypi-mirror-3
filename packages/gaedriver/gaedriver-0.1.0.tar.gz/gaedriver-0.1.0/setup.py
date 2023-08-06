#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Setup script for gaedriver."""

__author__ = 'schuppe@google.com (Robert Schuppenies)'

from distutils.core import setup
import os


PACKAGE_NAME = 'gaedriver'
LICENSE = 'Apache License 2.0'
DESCRIPTION = 'A tool for end-to-end testing of App Engine apps.'
URL = 'http://code.google.com/p/gaedriver'
AUTHOR = 'Robert Schuppenies'
AUTHOR_EMAIL = 'schuppe@google.com'
PLATFORMS = ['any']


def get_version():
    """Get the version of the current release.

    Returns:
      The version string.

    Raises:
      ValueError: If no valid VERSION file could be found.
    """
    this_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(this_dir, 'VERSION')
    version_fh = open(version_file)
    lines = version_fh.readlines()
    version_fh.close()
    for line in lines:
        if line.startswith('release:'):
            _, version = line.split(':')
            version = version.strip()
            version_parts = version.split(' ')
            return version_parts[0]
    raise ValueError('no line "release: ..." found in %s' % version_file)


def get_long_description():
    this_dir = os.path.abspath(os.path.dirname(__file__))
    readme_file = os.path.join(this_dir, 'README')
    return open(readme_file).read()


def main():
    setup(name=PACKAGE_NAME,
          version=get_version(),
          description=DESCRIPTION,
          long_description=get_long_description(),
          license=LICENSE,
          url=URL,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          platforms=PLATFORMS,
          packages=[PACKAGE_NAME],
          package_dir={PACKAGE_NAME: 'src/gaedriver'},
          )


if __name__ == '__main__':
    main()
