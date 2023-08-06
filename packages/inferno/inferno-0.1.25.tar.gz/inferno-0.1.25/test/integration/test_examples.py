# -*- coding: utf-8 -*-

import cStringIO
import os
import sys
import tempfile

from nose.tools import eq_

from inferno.lib.disco_ext import get_disco_handle
from inferno.lib.job_factory import JobFactory
from inferno.lib.settings import InfernoSettings


class TestExamples(object):

    json_data = """
{"first_name":"Homer", "last_name":"Simpson"}
{"first_name":"Manjula", "last_name":"Nahasapeemapetilon"}
{"first_name":"Herbert", "last_name":"Powell"}
{"first_name":"Ruth", "last_name":"Powell"}
{"first_name":"Bart", "last_name":"Simpson"}
{"first_name":"Apu", "last_name":"Nahasapeemapetilon"}
{"first_name":"Marge", "last_name":"Simpson"}
{"first_name":"Janey", "last_name":"Powell"}
{"first_name":"Maggie", "last_name":"Simpson"}
{"first_name":"Sanjay", "last_name":"Nahasapeemapetilon"}
{"first_name":"Lisa", "last_name":"Simpson"}
{"first_name":"Maggie", "last_name":"Términos"}
"""
    csv_data = """
Homer,Simpson
Manjula,Nahasapeemapetilon
Herbert,Powell
Ruth,Powell
Bart,Simpson
Apu,Nahasapeemapetilon
Marge,Simpson
Janey,Powell
Maggie,Simpson
Sanjay,Nahasapeemapetilon
Lisa,Simpson
Maggie,Términos
"""

    def setUp(self):
        sys.stdout = self.capture_stdout = cStringIO.StringIO()
        here = os.path.dirname(__file__)
        self.rules_dir = os.path.join(
            here, '..', '..', 'inferno', 'example_rules')
        self.tag = 'test:integration:chunk:users:2012-01-10'
        self.custom_tag_prefix = 'result:test:integration:last_names_result'
        self.result_tag_prefix = 'disco:job:results:last_names_result'

    def tearDown(self):
        sys.stdout = sys.__stdout__
        self.ddfs.delete(self.tag)
        for prefix in [self.custom_tag_prefix, self.result_tag_prefix]:
            for tag in self.ddfs.list(prefix):
                self.ddfs.delete(tag)

    def test_json(self):
        settings = InfernoSettings(
            rules_directory=self.rules_dir,
            immediate_rule='names.last_names_json')
        expected = [
            'last_name,count',
            'Nahasapeemapetilon,3',
            'Powell,3',
            'Simpson,5',
            'Términos,1']
        self._assert_integration_test(settings, expected, self.json_data)

    def test_csv(self):
        settings = InfernoSettings(
            rules_directory=self.rules_dir,
            immediate_rule='names.last_names_csv')
        expected = [
            'last_name,count',
            'Nahasapeemapetilon,3',
            'Powell,3',
            'Simpson,5',
            'Términos,1']
        self._assert_integration_test(settings, expected, self.csv_data)

    def test_many_keysets(self):
        settings = InfernoSettings(
            rules_directory=self.rules_dir,
            immediate_rule='names.first_and_last_names')
        expected = [
            'first_name,count',
            'Apu,1',
            'Bart,1',
            'Herbert,1',
            'Homer,1',
            'Janey,1',
            'Lisa,1',
            'Maggie,2',
            'Manjula,1',
            'Marge,1',
            'Ruth,1',
            'Sanjay,1',
            'last_name,count',
            'Nahasapeemapetilon,3',
            'Powell,3',
            'Simpson,5',
            'Términos,1']
        self._assert_integration_test(settings, expected, self.json_data)

    def test_tag_results(self):
        settings = InfernoSettings(
            rules_directory=self.rules_dir,
            immediate_rule='names.last_names_result')
        expected = [
            'last_name,count',
            'Nahasapeemapetilon,3',
            'Powell,3',
            'Simpson,5',
            'Términos,1']
        self._assert_integration_test(settings, expected, self.json_data)
        tags = self.ddfs.list(self.custom_tag_prefix)
        eq_(len(tags), 1)
        tags = self.ddfs.list(self.result_tag_prefix)
        eq_(len(tags), 1)

    def _chunk_test_data(self, settings, data):
        (_, name) = tempfile.mkstemp()
        with open(name, 'w') as f:
            f.write(data)
        self.settings = settings
        (_, self.ddfs) = get_disco_handle(settings['server'])
        self.ddfs.delete(self.tag)
        self.ddfs.chunk(self.tag, [name])

    def _assert_integration_test(self, settings, expected, data):
        self._chunk_test_data(settings, data)
        JobFactory.execute_immediate_rule(settings)
        actual = self.capture_stdout.getvalue()
        eq_(actual, '\r\n'.join(expected) + '\r\n')
