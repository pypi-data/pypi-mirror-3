.. -*- mode: rst -*-

==========================
python-unixtools
==========================

-------------------------------------------------------------
A set of Unix tools implemented in pure Python
-------------------------------------------------------------

:Author:  Hartmut Goebel <h.goebel@goebel-consult.de>
:Version: Version 0.0.1
:Copyright: GNU Public Licence v3 (GPLv3)
:Homepage: http://python-unixtools.origo.ethz.ch/

These tools are currently only meant as supplement to be able to use
distutils's sdist_tar, sdist_bztar and sdist_gztar on Windows/Wine.
Thus they currently only support the flags required by distutils.

But perhaps this will grow. Feel free to enhance. 

For more information please refer to the manpage or visit
the `project homepage <http://python-unixtools.origo.ethz.ch/>`_.


Requirements
~~~~~~~~~~~~~~~~~~~~

``python-unixtools`` requires

* Python 2.3 (tested with 2.5, but other versions should work, too),
* setuptools for installation (see below).


Installation
~~~~~~~~~~~~~~~~~~~

Installation Requirements
----------------------------

``python-unixtools`` uses setuptools for installation. Thus you need
either

* network access, so the install script will automatically download
  and install setuptools if they are not already installed

or

* the correct version of setuptools preinstalled using the
  `EasyInstall installation instructions
  <http://peak.telecommunity.com/DevCenter/EasyInstall#installation-instructions>`_.
  Those instructions also have tips for dealing with firewalls as well
  as how to manually download and install setuptools.


Installation 
-------------------------

Install ``python-unixtools`` by just running::

   python ./setup.py install



Custom Installation Locations
------------------------------

For installing to a custom location, use:

   # install to /usr/local/bin
   python ./setup.py install --prefix /usr/local

   # install to your Home directory (~/bin)
   python ./setup.py install --home ~


For more information about Custom Installation Locations please refer
to the `Custom Installation Locations Instructions
<http://peak.telecommunity.com/DevCenter/EasyInstall#custom-installation-locations>`_.
before installing ``python-unixtools``.
