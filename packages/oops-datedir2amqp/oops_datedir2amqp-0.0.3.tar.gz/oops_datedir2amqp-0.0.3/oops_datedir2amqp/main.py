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

"""Entry point for datedir2amqp."""

from functools import partial
import optparse
from textwrap import dedent
import sys

from amqplib import client_0_8 as amqp
import oops_amqp
import oops_datedir_repo

__all__ = ['main']


def main(argv=None):
    if argv is None:
        argv=sys.argv
    usage = dedent("""\
        %prog [options]

        The following options must be supplied:
         --exchange
         --host
         --username
         --password
         --vhost
         --repo

        e.g.
        datedir2amqp --exchange oopses --host "localhost:3472" \\
            --username "guest" --password "guest" --vhost "/" \\
            --repo "/srv/logs/local-oops"

        The AMQP exchange should be setup in advance. The repo should be the
        root directory that OOPS are being written too.

        When run this program will copy every OOPS in the repo to amqp,
        deleting each one after it is successfully sent. On failure the
        OOPS is left behind.
        """)
    description = "Load OOPS reports into AMQP from a DateDirRepo."
    parser = optparse.OptionParser(
        description=description, usage=usage)
    parser.add_option('--exchange', help="AMQP Exchange to send OOPSes too.")
    parser.add_option('--host', help="AQMP host / host:port.")
    parser.add_option('--username', help="AQMP username.")
    parser.add_option('--password', help="AQMP password.")
    parser.add_option('--vhost', help="AMQP vhost.")
    parser.add_option('--key', help="AMQP routing key to use.")
    parser.add_option('--repo', help="Path to the repository to read from.")
    options, args = parser.parse_args(argv[1:])
    def needed(optname):
        if getattr(options, optname, None) is None:
            raise ValueError('option "%s" must be supplied' % optname)
    needed('host')
    needed('exchange')
    needed('username')
    needed('password')
    needed('vhost')
    needed('repo')
    factory = partial(
        amqp.Connection, host=options.host, userid=options.username,
        password=options.password, virtual_host=options.vhost)
    publisher = oops_amqp.Publisher(factory, options.exchange, options.key, inherit_id=True)
    repo = oops_datedir_repo.DateDirRepo(options.repo)
    repo.republish(publisher)
