"""
A set of Unix tools implemented in pure Python.

These tools are currently only meant as supplement to be able to use
distutils's sdist_tar, sdist_bztar and sdist_gztar on Windows/Wine.
Thus they currently only support the flags required by distutils.

But perhaps this will grow. Feel free to enhance.
"""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "python-unixtools",
    version = "0.0.1",
    packages=['unixtools'],

    author = "Hartmut Goebel",
    author_email = "h.goebel@goebel-consult.de",
    description = "A set of Unix tools implemented in pure Python.",
    long_description = __doc__,
    license = "GPL 3.0",
    keywords = "tar bzip2 gzip",
    url          = "http://python-unixtools.origo.ethz.ch/",
    download_url = "http://python-unixtools.origo.ethz.ch/download/",
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ],

    # these are for easy_install (used by bdist_*)
    entry_points = {
        "console_scripts": [
            "tar   = unixtools.tar:main",
            "gzip  = unixtools.gzip:main",
            "bzip2 = unixtools.bzip2:main",
        ],
    },
)
