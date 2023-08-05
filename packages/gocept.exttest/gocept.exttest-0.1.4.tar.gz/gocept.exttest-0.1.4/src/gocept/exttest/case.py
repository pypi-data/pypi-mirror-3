# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import json
import subprocess
import unittest


def makeSuite(external_runner, *args):
    suite = unittest.TestSuite()
    job = subprocess.Popen(
        [external_runner, '--list'] + list(args),
        stdout=subprocess.PIPE)
    job.wait()
    output, error = job.communicate()
    result = json.loads(output)

    for testcase in result:
        suite.addTest(unittest.makeSuite(TestCase.create_from_external(
                    [external_runner] + list(args),
                    testcase['case'], testcase['tests'])))
    return suite


class TestCase(unittest.TestCase):

    @classmethod
    def create_from_external(cls, external_runner, testcase, tests):
        def make_testmethod(testcase, name):
            return lambda self: self._run_js_test(testcase, name)

        body = dict(runner=external_runner)
        for name in tests:
            method_name = 'test_' + name.replace(' ', '_')
            body[method_name] = make_testmethod(testcase, name)

        return type(
            testcase.encode('ascii') + 'Test',
            (cls,),
            body)

    def _run_js_test(self, testcase, testname):
        job = subprocess.Popen(
            self.runner + ['--run', testcase + '.' + testname],
            stdout=subprocess.PIPE)
        job.wait()
        output, error = job.communicate()
        result = json.loads(output)

        for case in result:
            if case['name'] != testcase + '.' + testname:
                continue

            status = case['status']
            if status == 'SUCCESS':
                return
            elif status == 'FAIL':
                self.fail(case['message'] + '\n' + case['traceback'])
            elif status == 'ERROR':
                raise RuntimeError(case['message'] + '\n' + case['traceback'])
            else:
                raise ValueError(
                    'JS test returned invalid test status %r' % status)
