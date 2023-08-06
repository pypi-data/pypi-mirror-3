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

import os
import unittest

import fixtures
import psycopg2
from van.pg import DatabaseManager
import testresources
import testtools

from pgbouncer.fixture import PGBouncerFixture

# A 'just-works' workaround for Ubuntu not exposing initdb to the main PATH.
os.environ['PATH'] = os.environ['PATH'] + ':/usr/lib/postgresql/8.4/bin'


def test_suite():
    loader = testresources.TestLoader()
    return loader.loadTestsFromName(__name__)


class ResourcedTestCase(testtools.TestCase, testresources.ResourcedTestCase):
    """Mix together testtools and testresources."""


def setup_user(db):
    conn = psycopg2.connect(host=db.host, database=db.database)
    conn.cursor().execute('CREATE USER user1')
    conn.commit()
    conn.close()


class TestFixture(ResourcedTestCase):

    resources = [('db', DatabaseManager(initialize_sql=setup_user))]

    def setUp(self):
        super(TestFixture, self).setUp()
        self.bouncer = PGBouncerFixture()
        self.bouncer.databases[self.db.database] = 'host=' + self.db.host
        self.bouncer.users['user1'] = ''

    def connect(self, host=None):
        return psycopg2.connect(
            host=(self.bouncer.host if host is None else host),
            port=self.bouncer.port, database=self.db.database,
            user='user1')

    def test_dynamic_port_allocation(self):
        self.useFixture(self.bouncer)
        self.connect().close()

    def test_stop_start_facility(self):
        # Once setup the fixture can be stopped, and started again, retaining
        # its configuration. [Note that dynamically allocated ports could
        # potentially be used by a different process, so this isn't perfect,
        # but its pretty reliable as a test helper, and manual port allocation
        # outside the dynamic range should be fine.
        self.useFixture(self.bouncer)
        self.bouncer.stop()
        self.assertRaises(psycopg2.OperationalError, self.connect)
        self.bouncer.start()
        self.connect().close()

    def test_unix_sockets(self):
        unix_socket_dir = self.useFixture(fixtures.TempDir()).path
        self.bouncer.unix_socket_dir = unix_socket_dir
        self.useFixture(self.bouncer)
        # Connect to pgbouncer via a Unix domain socket. We don't
        # care how pgbouncer connects to PostgreSQL.
        self.connect(host=unix_socket_dir).close()

    def test_is_running(self):
        # The is_running property indicates if pgbouncer has been started and
        # has not yet exited.
        self.assertFalse(self.bouncer.is_running)
        with self.bouncer:
            self.assertTrue(self.bouncer.is_running)
        self.assertFalse(self.bouncer.is_running)

    def test_dont_start_if_already_started(self):
        # If pgbouncer is already running, don't start another one.
        self.useFixture(self.bouncer)
        bouncer_pid = self.bouncer.process.pid
        self.bouncer.start()
        self.assertEqual(bouncer_pid, self.bouncer.process.pid)


if __name__ == "__main__":
    loader = testresources.TestLoader()
    unittest.main(testLoader=loader)
