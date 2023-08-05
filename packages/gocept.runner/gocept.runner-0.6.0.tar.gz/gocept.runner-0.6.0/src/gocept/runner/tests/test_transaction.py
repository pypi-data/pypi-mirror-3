# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.runner import transaction_per_item
import ZODB.POSException
import gocept.testing.assertion
import mock
import unittest


class TransactionPerItemTest(unittest.TestCase,
                             gocept.testing.assertion.Exceptions):

    def setUp(self):
        self.calls = mock.Mock()
        self.patches = []
        self.patch('transaction.commit', self.calls.commit)
        self.patch('transaction.abort', self.calls.abort)

        @transaction_per_item
        def example_func():
            yield self.calls.step1
            yield self.calls.step2
        self.example_func = example_func

    def tearDown(self):
        for patch in self.patches:
            patch.stop()

    def patch(self, *args):
        patch = mock.patch(*args)
        self.patches.append(patch)
        return patch.start()

    def test_calls_callables_and_commits_after_each(self):
        self.example_func()
        self.assertEqual(
            [('step1',),
             ('commit',),
             ('step2',),
             ('commit',)
             ], self.calls.method_calls)

    def test_on_exception_calls_abort_and_continues_with_next_item(self):
        self.calls.step1.side_effect = RuntimeError('provoked')
        self.example_func()
        self.assertEqual(
            [('step1',),
             ('abort',),
             ('step2',),
             ('commit',)
             ], self.calls.method_calls)

    def test_conflict_error_during_commit_aborts_and_is_swallowed(self):
        self.calls.commit.side_effect = ZODB.POSException.ConflictError()
        with self.assertNothingRaised():
            self.example_func()
        self.assertEqual(
            [('step1',),
             ('commit',),
             ('abort',),
             ('step2',),
             ('commit',),
             ('abort',),
             ], self.calls.method_calls)
