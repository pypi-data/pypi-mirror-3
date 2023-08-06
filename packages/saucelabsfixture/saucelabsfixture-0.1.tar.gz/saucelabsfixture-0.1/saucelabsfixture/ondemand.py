# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""SauceLabs' Sauce OnDemand fixture."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "SauceOnDemandFixture",
    ]

from fixtures import Fixture
from selenium import webdriver


class SauceOnDemandFixture(Fixture):
    """Start up a driver for SauceLabs' Sauce OnDemand service.

    See `Getting Started`_, the `Available Browsers List`_, and `Additional
    Configuration`_ to help configure this fixture.

    .. _Getting Started:
      http://saucelabs.com/docs/ondemand/getting-started/env/python/se2/linux

    .. _Available Browsers List:
      http://saucelabs.com/docs/ondemand/browsers/env/python/se2/linux

    .. _Additional Configuration:
      http://saucelabs.com/docs/ondemand/additional-config

    """

    # Default capabilities
    default_capabilities = {
        "video-upload-on-pass": False,
        "record-screenshots": False,
        "record-video": False,
        }

    def __init__(self, capabilities, control_url):
        """
        @param capabilities: A member of `webdriver.DesiredCapabilities`, plus
            any additional configuration.
        @param control_url: The URL, including username and API key for the
            Sauce OnDemand service, or a Sauce Connect service.
        """
        super(SauceOnDemandFixture, self).__init__()
        self.capabilities = self.default_capabilities.copy()
        self.capabilities.update(capabilities)
        self.control_url = control_url

    def setUp(self):
        super(SauceOnDemandFixture, self).setUp()
        self.driver = webdriver.Remote(
            desired_capabilities=self.capabilities,
            command_executor=self.control_url.encode("ascii"))
        self.driver.implicitly_wait(30)  # TODO: Is this always needed?
        self.addCleanup(self.driver.quit)
