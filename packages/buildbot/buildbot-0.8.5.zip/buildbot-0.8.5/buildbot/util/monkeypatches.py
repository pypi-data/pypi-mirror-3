# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import sys
import twisted
from twisted.trial import unittest

def add_debugging_monkeypatches():
    """
    DO NOT CALL THIS DIRECTLY

    This adds a few "harmless" monkeypatches which make it easier to debug
    failing tests.  It is called automatically by buildbot.test.__init__.
    """
    from twisted.application.service import Service
    old_startService = Service.startService
    old_stopService = Service.stopService
    def startService(self):
        assert not self.running
        return old_startService(self)
    def stopService(self):
        assert self.running
        return old_stopService(self)
    Service.startService = startService
    Service.stopService = stopService

    # versions of Twisted before 9.0.0 did not have a UnitTest.patch that worked
    # on Python-2.7
    if twisted.version.major <= 9 and sys.version_info[:2] == (2,7):
        def nopatch(self, *args):
            raise unittest.SkipTest('unittest.TestCase.patch is not available')
        unittest.TestCase.patch = nopatch
