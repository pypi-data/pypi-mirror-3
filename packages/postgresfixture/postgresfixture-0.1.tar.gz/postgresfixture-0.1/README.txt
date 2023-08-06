.. -*- mode: rst -*-

***************
postgresfixture
***************

A Python fixture for creating PostgreSQL clusters and databases, and
tearing them down again, intended for use during development and
testing.

For more information see the `Launchpad project page`_.

.. _Launchpad project page: https://launchpad.net/postgresfixture


Getting started
===============

Use like any other fixture::

  from contextlib import closing
  from postgresfixture import ClusterFixture

  def test_something(self):
      cluster = self.useFixture(ClusterFixture("db"))
      cluster.createdb("example")
      with closing(cluster.connect("example")) as conn:
          ...
      cluster.dropbdb("example")  # Optional.

This will create a new cluster, create a database called "example",
then tear it all down at the end; nothing will remain on disk. If you
want the cluster and its databases to remain on disk, pass
``preserve=True`` to the ``ClusterFixture`` constructor.


From the command line
=====================

Once this package is installed, you'll have a ``postgresfixture``
script. Alternatively you can use ``python -m postgresfixture`` to
achieve the same thing. Use ``--help`` to discover the options
available to you.
