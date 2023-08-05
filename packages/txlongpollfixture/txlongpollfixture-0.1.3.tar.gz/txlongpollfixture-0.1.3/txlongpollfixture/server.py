# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).


"""Testing fixture for txlongpoll."""

__metaclass__ = type

__all__ = [
    "TxLongPollFixture",
    ]

from collections import namedtuple
import os
import signal
import socket
import subprocess
import time

from fixtures import (
    Fixture,
    TempDir,
    )
from testtools.content import Content
from testtools.content_type import UTF8_TEXT


def preexec_fn():
    # Revert Python's handling of SIGPIPE. See
    # http://bugs.python.org/issue1652 for more info.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def allocate_ports(n=1):
    """Allocate `n` unused ports.

    There is a small race condition here (between the time we allocate the
    port, and the time it actually gets used), but for the purposes for which
    this function gets used it isn't a problem in practice.
    """
    sockets = map(lambda _: socket.socket(), xrange(n))
    try:
        for s in sockets:
            s.bind(('localhost', 0))
        return map(lambda s: s.getsockname()[1], sockets)
    finally:
        for s in sockets:
            s.close()


TxLongPollFixtureConfig= namedtuple(
    "TxLongPollFixtureConfig", (
        "broker_user", "broker_password", "broker_vhost", "frontend_port",
        "broker_host", "broker_port", "twistd_bin", "logfile",
        "queue_prefix"))


class TxLongPollFixture(Fixture):
    """A txlongpoll server fixture.

    When set up, a txlongpoll service will be started and shut down when
    the fixture is cleaned up.

    :ivar broker_user: The user name to log into RabbitMQ's broker with.
    :ivar broker_password: The password to log into RabbitMQ's broker with.
    :ivar frontend_port: The server port on which to accept incoming HTTP
        requests
    :ivar broker_vhost: The vhost to use in the RabbitMQ server.
    :ivar broker_host: The name of the host running the RabbitMQ server.
    :ivar broker_host: The port on the host running the RabbitMQ server.
    :ivar twistd_bin: The path to the twistd binary (defaults to 'twistd').
    :ivar logfile: Where to write the log file for the txlongpoll server.
    :ivar queue_prefix: What prefix to assign to all queue names used by
        txlongpoll.
    """

    def __init__(self, broker_user, broker_password, broker_vhost,
                 frontend_port=None, broker_host="localhost",
                 broker_port=5672, twistd_bin='twistd', logfile=None,
                 queue_prefix=""):
        super(TxLongPollFixture, self).__init__()
        self.config = TxLongPollFixtureConfig(
            broker_user=broker_user,
            broker_password=broker_password,
            frontend_port=frontend_port,
            broker_vhost=broker_vhost,
            broker_host=broker_host,
            broker_port=broker_port,
            twistd_bin=twistd_bin,
            logfile=logfile,
            queue_prefix=queue_prefix)

    def setUp(self):
        super(TxLongPollFixture, self).setUp()
        self.tempdir = self.useFixture(TempDir()).path
        if self.config.frontend_port is None:
            self.config = self.config._replace(
                frontend_port=allocate_ports(1)[0])
        if self.config.logfile is None:
            self.config = self.config._replace(
                logfile=os.path.join(self.tempdir, "txlongpollfixture.log"))
        self._start()

    def _start(self):
        cmd = (
            self.config.twistd_bin, "-n",
            "txlongpoll",
            "-l", self.config.logfile,
            "-p", str(self.config.broker_port),
            "-h", self.config.broker_host,
            "-u", self.config.broker_user,
            "-a", self.config.broker_password,
            "-v", self.config.broker_vhost,
            "-f", str(self.config.frontend_port),
            "-x", self.config.queue_prefix,
            )

        with open(self.config.logfile, "wb") as logfile:
            with open(os.devnull, "rb") as devnull:
                self.process = subprocess.Popen(
                    cmd, stdin=devnull, stdout=logfile, stderr=logfile,
                    cwd=self.tempdir, preexec_fn=preexec_fn)

        # Check to see that it actually started up.
        timeout = time.time() + 5
        while time.time() < timeout:
            if self.is_running:
                break
            time.sleep(0.1)
        else:
            raise Exception("Timeout waiting for txlongpoll to start.")
        self.addCleanup(self._stop)

        # Keep the logfile open so even if it's deleted we can read it
        # later.
        open_logfile = open(self.config.logfile, "rb")
        self.addDetail(
            os.path.basename(self.config.logfile),
            Content(UTF8_TEXT, lambda: open_logfile))

    @property
    def is_running(self):
        """Is the txlongpoll server up and accepting requests?"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("localhost", self.config.frontend_port))
        except socket.error:
            s.close()
            return False

        s.close()
        return True

    @property
    def is_process_up(self):
        """Is the txlongpoll server process running?"""
        if self.process is None:
            return False
        else:
            return self.process.poll() is None

    def _stop(self):
        timeout = time.time() + 5
        while time.time() < timeout:
            if not self.is_process_up:
                break
            self.process.terminate()
            time.sleep(0.1)
        else:
            # Kill it hard.
            if self.is_process_up:
                self.process.kill()
                time.sleep(0.5)
            if self.is_running:
                raise Exception("txlongpoll server just won't die.")

