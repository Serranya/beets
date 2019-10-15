# -*- coding: utf-8 -*-
# This file is part of beets.
# Copyright 2019, Carl Suster
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Test the beets.export utilities associated with the export plugin.
"""

from __future__ import division, absolute_import, print_function

import unittest
from test.helper import TestHelper
import re  # used to test csv format
import json
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET


class ExportPluginTest(unittest.TestCase, TestHelper):
    def setUp(self):
        self.setup_beets()
        self.load_plugins('export')
        self.test_values = {'title': 'xtitle', 'album': 'xalbum'}

    def tearDown(self):
        self.unload_plugins()
        self.teardown_beets()

    def execute_command(self, format_type, artist):
        query = ','.format(list(self.test_values.keys()))
        actual = self.run_with_output(
            'export',
            '-f', format_type,
            '-i', query,
            artist
        )
        return re.sub("\\s+", '', actual)

    def create_item(self):
        item, = self.add_item_fixtures()
        item.artist = 'xartist'
        item.title = self.test_values['title']
        item.album = self.test_values['album']
        item.write()
        item.store()
        return item

    def test_json_output(self):
        item1 = self.create_item()
        out = self.run_with_output(
            'export',
            '-f', 'json',
            '-i', 'album,title',
            item1.artist
        )
        json_data = json.loads(out)[0]
        for key, val in self.test_values.items():
            self.assertTrue(key in json_data)
            self.assertEqual(val, json_data[key])

    def test_csv_output(self):
        item1 = self.create_item()
        out = self.run_with_output(
            'export',
            '-f', 'csv',
            '-i', 'album,title',
            item1.artist
        )
        csv_list = re.split('\r', re.sub('\n', '', out))
        head = re.split(',', csv_list[0])
        vals = re.split(',|\r', csv_list[1])
        for index, column in enumerate(head):
            self.assertTrue(self.test_values.get(column, None) is not None)
            self.assertEqual(vals[index], self.test_values[column])

    def test_xml_output(self):
        item1 = self.create_item()
        out = self.run_with_output(
            'export',
            '-f', 'xml',
            '-i', 'album,title',
            item1.artist
        )
        library = ET.fromstring(out)
        self.assertIsInstance(library, Element)
        for track in library[0]:
            for details in track:
                tag = details.tag
                txt = details.text
                self.assertTrue(tag in self.test_values, msg=tag)
                self.assertEqual(self.test_values[tag], txt, msg=txt)

    def check_assertin(self, actual, str_format, key, val):
        expected = str_format.format(key, val)
        self.assertIn(
            expected,
            actual
        )


def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

"""
    def test_csv_output(self):
        item1 = self.create_item()
        actual = self.execute_command(
            format_type='csv',
            artist=item1.artist
        )
        for key, val in self.test_values.items():
            self.check_assertin(
                actual=actual,
                str_format='{0}{1}',
                key='',
                val=val
            )

    def test_xml_output(self):
        item1 = self.create_item()
        actual = self.execute_command(
            format_type='xml',
            artist=item1.artist
        )
        for key, val in self.test_values.items():
            self.check_assertin(
                actual=actual,
                str_format='<{0}>{1}</{0}>',
                key=key,
                val=val
            )

    def test_json_output(self):
        item1 = self.create_item()
        actual = self.execute_command(
            format_type='json',
            artist=item1.artist
        )
        for key, val in self.test_values.items():
            self.check_assertin(
                actual=actual,
                str_format='"{0}":"{1}"',
                key=key,
                val=val
            )
"""
