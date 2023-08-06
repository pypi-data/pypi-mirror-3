#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Republish OOPS reports from a DateDirRepo over AMQP.

Run the script::

  $ bin/datedir2amqp --host XX --username XX --password XX --vhost XX \
    --exchange XX --repo XX

Note that the repo should be the same path you are supplying to your
DateDirRepo in whatever process is creating OOPSes.

A common use for this setup is as a fallback: in your application report to
AMQP directly, with a DateDirRepo configured as fallback, then use datedir2amqp
to pickup and respool any OOPS reports that were generated while your AMQP
server is unavailable.
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
__version__ = (0, 0, 4, 'final', 0)

__all__ = [
    'main',
    ]

from oops_datedir2amqp.main import main
