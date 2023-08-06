#  zope_fixtures: Zope fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2011, Robert Collins <robertc@robertcollins.net>
# 
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

__all__ = [
    'ComponentsFixture',
    'UtilityFixture',
    ]

from fixtures import Fixture
from testtools.helpers import try_import

Components = try_import("zope.component.registry.Components")
getSiteManager = try_import("zope.component.getSiteManager")


class ComponentsFixture(Fixture):
    """Overlay the global Zope registry so that tests don't change it.

    :ivar registry: An alternate Zope registry that can be used to override
        registrations in the original registry. This isn't normally needed:
        once setUp you can access the registry by calling getSiteManager()
        as normal.

    Example::

        class TestSomething(TestCase):

            def test_registry(self):
                self.useFixture(ComponentsFixture())
                getSiteManager().registerUtility(...)
                # more code here
    """

    def __init__(self, bases=None):
        """Initialize the fixture.

        :param bases: The registries that should be used as bases for the
            fixture's registry. The default is to base on the current
            global site manager, as returned by getSiteManager().
        """
        super(ComponentsFixture, self).__init__()
        if bases is None:
            bases = (getSiteManager(),)
        self._bases = bases

    def setUp(self):
        super(ComponentsFixture, self).setUp()
        self.registry = Components(bases=self._bases)
        if getSiteManager.implementation is not getSiteManager.original:
            self.addCleanup(getSiteManager.sethook, getSiteManager.implementation)
        getSiteManager.sethook(lambda context=None: self.registry)
        self.addCleanup(getSiteManager.reset)


class UtilityFixture(Fixture):
    """Convenience around ComponentsFixture to override a single utility."""

    def __init__(self, *args, **kwargs):
        """Create an UtilityFixture.

        The args and kwargs parameters are the same supported by
        registerUtility and will be passed to it.
        """
        super(UtilityFixture, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def setUp(self):
        super(UtilityFixture, self).setUp()
        components = self.useFixture(ComponentsFixture())
        components.registry.registerUtility(*self.args, **self.kwargs)
