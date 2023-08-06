from twisted.trial.unittest import TestCase

from txaws.server.method import Method


class MethodTestCase(TestCase):

    def setUp(self):
        super(MethodTestCase, self).setUp()
        self.method = Method()

    def test_defaults(self):
        """
        By default a L{Method} applies to all API versions and handles a
        single action matching its class name.
        """
        self.assertIdentical(None, self.method.actions)
        self.assertIdentical(None, self.method.versions)
