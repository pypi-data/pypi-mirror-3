#!/usr/bin/env python

from distutils.core import setup
import os.path

description = file(os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="anonymiseip",
      version="0.0.1",
      description="Web service for IP anonymisation.",
      long_description=description,
      maintainer="Robert Collins",
      maintainer_email="robert.collins@canonical.com",
      url="https://launchpad.net/anonymiseip",
      packages=['anonymiseip'],
      package_dir = {'':'.'},
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      install_requires = [
      ],
      )
