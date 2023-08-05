# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.exttest.case import makeSuite
import mock
import unittest


class FindTest(unittest.TestCase):

    @mock.patch('subprocess.Popen')
    def test_builds_test_case_classes_from_list_output(self, popen):
        popen().communicate.return_value = (
            '[{"case":"Reality","tests":["exists","fails"]}]', 0)
        combined_suite = makeSuite(
            mock.sentinel.runner, mock.sentinel.directory)
        self.assertEqual(mock.sentinel.directory, popen.call_args[0][0][2])
        self.assertEqual(2, combined_suite.countTestCases())
        test_suite = iter(combined_suite).next()
        suite = iter(test_suite)
        test = suite.next()
        self.assertEqual(
            'test_exists (gocept.exttest.case.RealityTest)', str(test))
        with mock.patch.object(test, '_run_js_test') as run:
            test()
            run.assert_called_with('Reality', 'exists')

        test = suite.next()
        self.assertEqual(
            'test_fails (gocept.exttest.case.RealityTest)', str(test))
        with mock.patch.object(test, '_run_js_test') as run:
            test()
            run.assert_called_with('Reality', 'fails')
