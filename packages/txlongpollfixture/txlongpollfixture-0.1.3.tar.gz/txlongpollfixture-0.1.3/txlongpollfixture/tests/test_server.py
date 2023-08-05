# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for txlongpollfixture."""

__metaclass__ = type

import os
import socket

from testtools import (
    ExpectedException,
    TestCase,
    )
from testtools.testcase import gather_details
from txlongpollfixture.server import TxLongPollFixture


class TestTxLongPollFixture(TestCase):

    def setUp(self):
        super(TestTxLongPollFixture, self).setUp()
        self.twistd_bin = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir,
            "bin", "twistd-for-txlongpoll")

    def test_start_and_stop(self):
        fixture = TxLongPollFixture(
            broker_user="guest",
            broker_password="guest",
            frontend_port=9999,
            broker_vhost="/",  # "/" is the default vhost
            broker_host="localhost",
            broker_port=5672,
            twistd_bin=self.twistd_bin,
            )

        with fixture:
            try:
                # Try and connect to the frontend port.
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Will raise socket.error if the fixture is not up.
                s.connect(("localhost", fixture.config.frontend_port))
                s.close()
            except Exception:
                # self.useFixture() is not being used because we want to
                # handle the fixture's lifecycle, so we must also be
                # responsible for propagating fixture details.
                gather_details(fixture.getDetails(), self.getDetails())
                raise

        # It should be down now.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with ExpectedException(socket.error, '.*'):
            s.connect(("localhost", fixture.config.frontend_port))

    def test_port_allocation(self):
        fixture = TxLongPollFixture(
            broker_user="guest",
            broker_password="guest",
            broker_vhost="/",
            broker_host="localhost",
            broker_port=5672,
            twistd_bin=self.twistd_bin,
            )

        with fixture:
            self.assertIsInstance(fixture.config.frontend_port, int)
