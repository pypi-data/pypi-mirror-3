# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Manage a PostgreSQL cluster."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "main",
    ]

import argparse
from itertools import imap
from os import (
    environ,
    fdopen,
    )
import pipes
import signal
from subprocess import CalledProcessError
import sys
from time import sleep

from postgresfixture.clusterfixture import ClusterFixture


def setup():
    # Ensure stdout and stderr are line-bufferred.
    sys.stdout = fdopen(sys.stdout.fileno(), "ab", 1)
    sys.stderr = fdopen(sys.stderr.fileno(), "ab", 1)
    # Run the SIGINT handler on SIGTERM; `svc -d` sends SIGTERM.
    signal.signal(signal.SIGTERM, signal.default_int_handler)


def repr_pid(pid):
    if isinstance(pid, int) or pid.isdigit():
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as fd:
                cmdline = fd.read().rstrip("\0").split("\0")
        except IOError:
            return "%s (*unknown*)" % pid
        else:
            return "%s (%s)" % (
                pid, " ".join(imap(pipes.quote, cmdline)))
    else:
        return pipes.quote(pid)


def locked_by_description(lock):
    pids = sorted(lock.locked_by)
    return "locked by:\n* %s" % (
        "\n* ".join(imap(repr_pid, pids)))


def error(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    return print(*args, **kwargs)


def get_database_name(default="data"):
    """Return the desired database name, used by some commands.

    Obtained from the ``PGDATABASE`` environment variable.
    """
    return environ.get("PGDATABASE", default)


def action_destroy(cluster):
    """Destroy a cluster."""
    action_stop(cluster)
    cluster.destroy()
    if cluster.exists:
        if cluster.lock.locked:
            message = "%s: cluster is %s" % (
                cluster.datadir, locked_by_description(cluster.lock))
        else:
            message = "%s: cluster could not be removed." % cluster.datadir
        error(message)
        raise SystemExit(2)


def action_run(cluster):
    """Create and run a cluster.

    If specified in the ``PGDATABASE`` environment variable, a database will
    also be created within the cluster.
    """
    database_name = get_database_name(default=None)
    with cluster:
        if database_name is not None:
            cluster.createdb(database_name)
        while cluster.running:
            sleep(5.0)


def action_shell(cluster):
    """Spawn a ``psql`` shell for a database in the cluster.

    The database name can be specified in the ``PGDATABASE`` environment
    variable.
    """
    database_name = get_database_name()
    with cluster:
        cluster.createdb(database_name)
        cluster.shell(database_name)


def action_status(cluster):
    """Display a message about the state of the cluster.

    The return code is also set:

    - 0: cluster is running.
    - 1: cluster exists, but is not running.
    - 2: cluster does not exist.

    """
    if cluster.exists:
        if cluster.running:
            print("%s: running" % cluster.datadir)
            raise SystemExit(0)
        else:
            print("%s: not running" % cluster.datadir)
            raise SystemExit(1)
    else:
        print("%s: not created" % cluster.datadir)
        raise SystemExit(2)


def action_stop(cluster):
    """Stop a cluster."""
    cluster.stop()
    if cluster.running:
        if cluster.lock.locked:
            message = "%s: cluster is %s" % (
                cluster.datadir, locked_by_description(cluster.lock))
        else:
            message = "%s: cluster is still running." % cluster.datadir
        error(message)
        raise SystemExit(2)


actions = {
    "destroy": action_destroy,
    "run": action_run,
    "shell": action_shell,
    "status": action_status,
    "stop": action_stop,
    }


argument_parser = argparse.ArgumentParser(description=__doc__)
argument_parser.add_argument(
    "action", choices=sorted(actions), nargs="?", default="shell",
    help="the action to perform (default: %(default)s)")
argument_parser.add_argument(
    "-D", "--datadir", dest="datadir", action="store_true",
    default="db", help=(
        "the directory in which to place, or find, the cluster "
        "(default: %(default)s)"))
argument_parser.add_argument(
    "--preserve", dest="preserve", action="store_true",
    default=False, help=(
        "preserve the cluster and its databases when exiting, "
        "even if it was necessary to create and start it "
        "(default: %(default)s)"))


def main(args=None):
    args = argument_parser.parse_args(args)
    try:
        setup()
        action = actions[args.action]
        cluster = ClusterFixture(
            datadir=args.datadir, preserve=args.preserve)
        action(cluster)
    except CalledProcessError, error:
        raise SystemExit(error.returncode)
    except KeyboardInterrupt:
        pass
