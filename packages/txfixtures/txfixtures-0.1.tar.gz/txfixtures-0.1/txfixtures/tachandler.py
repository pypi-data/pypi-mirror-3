# Copyright 2009-2011 Canonical Ltd.  This software is licensed under the
# GNU General Public License version 3.

"""Test harness for TAC (Twisted Application Configuration) files."""

__metaclass__ = type

__all__ = [
    'TacTestSetup',
    'TacException',
    ]


import errno
import os
import socket
import subprocess
import sys
import time
import warnings

from fixtures import Fixture

from .osutils import (
    get_pid_from_file,
    kill_by_pidfile,
    two_stage_kill,
    until_no_eintr,
    )


# Can be overridden to specify path, etc.
twistd_script = 'twistd'


class TacException(Exception):
    """Error raised by TacTestSetup."""


class TacTestSetup(Fixture):
    """Setup an TAC file as daemon for use by functional tests.

    You must override setUpRoot to set up a root directory for the daemon.

    You may override _hasDaemonStarted, typically by calling _isPortListening, to 
    tell how long to wait before the daemon is available.
    """

    def setUp(self, spew=False, umask=None):
        Fixture.setUp(self)
        if get_pid_from_file(self.pidfile):
            # An attempt to run while there was an existing live helper
            # was made. Note that this races with helpers which use unique
            # roots, so when moving/eliminating this code check subclasses
            # for workarounds and remove those too.
            pid = get_pid_from_file(self.pidfile)
            warnings.warn("Attempt to start Tachandler %r with an existing "
                "instance (%d) running in %s." % (
                self.tacfile, pid, self.pidfile),
                UserWarning, stacklevel=2)
            two_stage_kill(pid)
            # If the pid file still exists, it may indicate that the process
            # respawned itself, or that two processes were started (race?) and
            # one is still running while the other has ended, or the process
            # was killed but it didn't remove the pid file (bug), or the
            # machine was hard-rebooted and the pid file was not cleaned up
            # (bug again). In other words, it's not safe to assume that a
            # stale pid file is safe to delete without human intervention.
            if get_pid_from_file(self.pidfile):
                raise TacException(
                    "Could not kill stale process %s." % (self.pidfile,))

        self.setUpRoot()
        args = [twistd_script, '-o', '-y', self.tacfile,
                '--pidfile', self.pidfile, '--logfile', self.logfile]
        if spew:
            args.append('--spew')
        if umask is not None:
            args.extend(('--umask', umask))

        # 2010-04-26, Salgado, http://pad.lv/570246: Deprecation warnings
        # in Twisted are not our problem.  They also aren't easy to suppress,
        # and cause test failures due to spurious stderr output.  Just shut
        # the whole bloody mess up.
        subprocess_env = dict(os.environ)
        subprocess_env['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'

        # Run twistd, and raise an error if the return value is non-zero or
        # stdout/stderr are written to.
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=subprocess_env)
        self.addCleanup(self.killTac)
        stdout = until_no_eintr(10, proc.stdout.read)
        if stdout:
            raise TacException('Error running %s: unclean stdout/err: %s'
                               % (args, stdout))
        rv = proc.wait()
        if rv != 0:
            raise TacException('Error %d running %s' % (rv, args))

        self._waitForDaemonStartup()

    def _hasDaemonStarted(self):
        """Has the daemon started?
        """
        return self._isPortListening('localhost', self.daemon_port)

    def _isPortListening(self, host, port):
        """True if a tcp port is accepting connections.

        This can be used by subclasses overriding _hasDaemonStarted, if they
        want to check the port is up rather than for the contents of the log
        file.
        """
        try:
            s = socket.socket()
            s.settimeout(2.0)
            s.connect((host, port))
            s.close()
            return True
        except socket.error, e:
            if e.errno == errno.ECONNREFUSED:
                return False
            else:
                raise

    def _waitForDaemonStartup(self):
        """ Wait for the daemon to fully start.

        Times out after 20 seconds.  If that happens, the log file content
        will be included in the exception message for debugging purpose.

        :raises TacException: Timeout.
        """
        # Watch the log file for readyservice.LOG_MAGIC to signal that startup
        # has completed.
        now = time.time()
        deadline = now + 20
        while now < deadline and not self._hasDaemonStarted():
            time.sleep(0.1)
            now = time.time()

        if now >= deadline:
            raise TacException('Unable to start %s. Content of %s:\n%s' % (
                self.tacfile, self.logfile, open(self.logfile).read()))

    def tearDown(self):
        # For compatibility - migrate to cleanUp.
        self.cleanUp()

    def killTac(self):
        """Kill the TAC file if it is running."""
        pidfile = self.pidfile
        kill_by_pidfile(pidfile)

    def sendSignal(self, sig):
        """Send the given signal to the tac process."""
        pid = get_pid_from_file(self.pidfile)
        if pid is None:
            return
        os.kill(pid, sig)

    def setUpRoot(self):
        """Override this.

        This should be able to cope with the root already existing, because it
        will be left behind after each test in case it's needed to diagnose a
        test failure (e.g. log files might contain helpful tracebacks).
        """
        raise NotImplementedError

    @property
    def root(self):
        raise NotImplementedError

    @property
    def tacfile(self):
        raise NotImplementedError

    @property
    def pidfile(self):
        raise NotImplementedError

    @property
    def logfile(self):
        raise NotImplementedError

    @property
    def daemon_port(self):
        raise NotImplementedError

def get_pid_from_file(pidfile_path):
    """Retrieve the PID from the given file, if it exists, None otherwise."""
    if not os.path.exists(pidfile_path):
        return None
    # Get the pid.
    pid = open(pidfile_path, 'r').read().split()[0]
    try:
        pid = int(pid)
    except ValueError:
        # pidfile contains rubbish
        return None
    return pid


