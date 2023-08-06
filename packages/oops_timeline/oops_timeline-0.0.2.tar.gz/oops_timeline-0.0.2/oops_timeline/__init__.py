# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""oops <-> timeline integration.

The oops_timeline package provides integration glue between timeline objects
(http://pypi.python.org/pypi/timeline) and the oops error reporting system
(http://pypi.python.org/pypi/oops).

Dependencies
============

* Python 2.6+

* oops (http://pypi.python.org/pypi/oops)

* timeline (http://pypi.python.org/pypi/timeline)

Testing Dependencies
====================

* subunit (http://pypi.python.org/pypi/python-subunit) (optional)

* testtools (http://pypi.python.org/pypi/testtools)

Usage
=====

oops_timeline provides an oops on_create hook to extract timeline data from
oops_context['timeline'] and inject it into the oops report as primitive data.

* Setup your configuration::

  >>> from oops import Config
  >>> config = Config()

Note that you will probably want at least one publisher, or your reports will
be discarded.

* Add in the timneline hook to the config::

  >>> oops_timeline.install_hooks(config)

This is a convenience function in case additional hooks are needed in future.

For more information see pydoc oops_timeline.

Installation
============

Either run setup.py in an environment with all the dependencies available, or
add the working directory to your PYTHONPATH.

Development
===========

Upstream development takes place at https://launchpad.net/python-oops-timeline.
To setup a working area for development, if the dependencies are not
immediately available, you can use ./bootstrap.py to create bin/buildout, then
bin/py to get a python interpreter with the dependencies available.

To run the tests use the runner of your choice, the test suite is
oops.tests.test_suite.

For instance::

  $ bin/py -m testtools.run oops_timeline.tests.test_suite
"""


# same format as sys.version_info: "A tuple containing the five components of
# the version number: major, minor, micro, releaselevel, and serial. All
# values except releaselevel are integers; the release level is 'alpha',
# 'beta', 'candidate', or 'final'. The version_info value corresponding to the
# Python version 2.0 is (2, 0, 0, 'final', 0)."  Additionally we use a
# releaselevel of 'dev' for unreleased under-development code.
#
# If the releaselevel is 'alpha' then the major/minor/micro components are not
# established at this point, and setup.py will use a version of next-$(revno).
# If the releaselevel is 'final', then the tarball will be major.minor.micro.
# Otherwise it is major.minor.micro~$(revno).
__version__ = (0, 0, 1, 'beta', 0)

__all__ = [
    'install_hooks',
    ]

from oops_timeline.hooks import install_hooks
