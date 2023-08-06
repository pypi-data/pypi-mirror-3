.. -*- mode: rst -*-

****************
saucelabsfixture
****************

A Python fixture for working with SauceLabs' services.

For more information see the `Launchpad project page`_.

.. _Launchpad project page: https://launchpad.net/saucelabsfixture


Getting started
===============

Use like any other fixture::

  from saucelabsfixture import (
      SauceConnectFixture,
      SauceOnDemandFixture,
      )

  capabilities = {...}

  def test_something(self):
      connect = self.useFixture(SauceConnectFixture())
      on_demand = SauceOnDemandFixture(
          capabilities, connect.control_url)
      self.useFixture(on_demand)
      driver = on_demand.driver
      ...

This will start up a Connect service using your credentials (see
below). It will also download ``Sauce-Connect.jar`` if it's not
already available. The driver will be set up to send commands via the
secure tunnel that the Connect service provides.


Credentials for the Connect service
===================================

Credentials for the Connect service can be passed into the
``SauceConnectFixture`` constructor, but otherwise they can be put
into a file in your home directory::

  $ mkdir -p ~/.saucelabs/connect
  $ touch ~/.saucelabs/connect/credentials
  $ chmod go-rwx ~/.saucelabs/connect/credentials
  $ echo "$username $api_key" > ~/.saucelabs/connect/credentials
