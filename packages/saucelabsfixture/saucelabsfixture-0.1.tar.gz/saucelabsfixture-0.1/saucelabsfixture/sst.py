# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""SauceLabs' Sauce OnDemand fixture for SST."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "SSTOnDemandFixture",
    ]

from saucelabsfixture.ondemand import SauceOnDemandFixture
from testtools.monkey import MonkeyPatcher


class SSTOnDemandFixture(SauceOnDemandFixture):
    """Variant of `SauceOnDemandFixture` that also patches `sst`.

    When this fixture is active you can use `sst` with the allocated driver
    without calling `sst.actions.start` or `sst.actions.stop`.
    """

    noop = staticmethod(lambda *args, **kwargs: None)

    def setUp(self):
        from sst import actions
        super(SSTOnDemandFixture, self).setUp()
        patcher = MonkeyPatcher(
            (actions, "browser", self.driver),
            (actions, "browsermob_proxy", None),
            (actions, "start", self.noop),
            (actions, "stop", self.noop))
        self.addCleanup(patcher.restore)
        patcher.patch()
