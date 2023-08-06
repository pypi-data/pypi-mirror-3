from bzrlib.tests import TestCase

from bzrlib.plugins.colo import trace

class TestTrace(TestCase):

    def setUp(self):
        # clear an existing setting of colo.debug
        TestCase.setUp(self)
        trace.DEBUG = True

    def test_mutter(self):
        trace.mutter('a message')
        log = self.get_log()
        self.assertContainsRe(log, 'bzr-colo: a message')

    def test_mutter_parametrized(self):
        trace.mutter('a %s message', 'parametrized')
        log = self.get_log()
        self.assertContainsRe(log, 'bzr-colo: a parametrized message')

    def test_no_mutter(self):
        trace.DEBUG = False
        trace.mutter('dont print me')
        log = self.get_log()
        self.assertNotContainsRe(log, 'bzr-colo: ')

