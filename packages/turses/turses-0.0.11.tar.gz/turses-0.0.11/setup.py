# -*- coding: utf-8 -*-

from distutils.core import setup

import turses


name = "turses"

requirements = [
    "httplib2",
    "oauth2",
    "python-twitter",
    "simplejson",
    "urwid",
]
test_requirements = list(requirements)
test_requirements.extend(["mock", "nose", "coverage", "nose-progressive"])

try:
    long_description = open("README.rst").read() + "\n\n" + open("HISTORY.rst").read()
except IOError:
    long_description = ""

setup(name="turses",
      version=turses.__version__,
      author="Alejandro Gómez",
      author_email="alejandroogomez@gmail.com",
      license="GPLv3",
      description="A Twitter client with a curses interface.",
      long_description=long_description,
      keywords="twitter client curses",
      packages=[
          "turses", 
          "turses.ui",
          "turses.api",
      ],
      package_data={'': ['LICENSE']},
      include_package_data=True,
      package_dir={
          "turses":  "turses"
      },
      scripts=["bin/turses"],
      platforms=["linux"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console :: Curses",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2",
      ],
      install_requires=requirements,
      tests_require=test_requirements,)
