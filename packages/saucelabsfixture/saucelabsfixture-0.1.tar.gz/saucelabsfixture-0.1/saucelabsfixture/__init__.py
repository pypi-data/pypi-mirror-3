# Copyright 2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""SauceLabs' Sauce OnDemand fixtures."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "SauceConnectFixture",
    "SauceOnDemandFixture",
    "SSTOnDemandFixture",
    "TimeoutException",
    ]


from saucelabsfixture.connect import (
    SauceConnectFixture,
    TimeoutException,
    )
from saucelabsfixture.ondemand import SauceOnDemandFixture
from saucelabsfixture.sst import SSTOnDemandFixture
