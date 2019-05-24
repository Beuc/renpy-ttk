#!/usr/bin/python

# Tests for Ren'Py translate blocks parser

# Copyright (C) 2019  Sylvain Beucler

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest
import tlparser

class TestTlparser(unittest.TestCase):

    def test_is_empty(self):
        self.assertTrue(tlparser.is_empty(''))
        self.assertTrue(tlparser.is_empty('\n'))
        self.assertFalse(tlparser.is_empty('translate french start_a170b500\n'))
        self.assertFalse(tlparser.is_empty('# game/script.rpy:27'))

    def test_is_comment(self):
        self.assertTrue(tlparser.is_comment('#'))
        self.assertTrue(tlparser.is_comment('# game/script.rpy:27\n'))
        self.assertFalse(tlparser.is_comment(' '))
        self.assertFalse(tlparser.is_comment('e "Hello"'))
        self.assertFalse(tlparser.is_comment('translate french start_a170b500  # test\n'))

    def test_is_block_start(self):
        self.assertTrue(tlparser.is_block_start('translate french start_a170b500  # test\n'))
    def test_extract_source(self):
        self.assertEqual(tlparser.extract_source('# game/script.rpy:27\n'), 'game/script.rpy:27')

    def test_extract_dqstrings(self):
        testcase = r'''    _( 'string " character' ) "Tricky single/double '\" multiple strings 2"'''
        self.assertEqual(tlparser.extract_dqstrings(testcase),
            [{'start': 31, 'end': 74, 'text': r'''Tricky single/double '\" multiple strings 2'''}])
        testcase = r'''_( "string \" character" ) "Tricky double/double \"' multiple strings"'''
        self.assertEqual(tlparser.extract_dqstrings(testcase),
            [{'start':  4, 'end': 23, 'text': r'''string \" character'''},
             {'start': 28, 'end': 69, 'text': r'''Tricky double/double \"' multiple strings'''}])

    def test_extract_base_string(self):
        self.assertEqual(
            tlparser.extract_base_string('''    old "menu title"\n'''),
            {'start': 9, 'end': 19, 'text': 'menu title'})

    def test_extract_dialog_string(self):
        self.assertEqual(
            tlparser.extract_dialog_string('''e "You've created a new Ren'Py game."\n'''),
            {'start': 3, 'end': 36, 'text': "You've created a new Ren'Py game."})
        testcase = r'''    _( 'string " character' ) "Tricky single/double '\" multiple strings 2"'''
        self.assertEqual(tlparser.extract_dialog_string(testcase),
            {'start': 31, 'end': 74, 'text': r'''Tricky single/double '\" multiple strings 2'''})

    def test_parse_next_block(self):
        # https://www.renpy.org/doc/html/translation.html
        lines = """
# TODO: Translation updated at 2019-05-18 19:13

# game/script.rpy:27
translate pot start_a170b500:

    # e "You've created a new Ren'Py game."
    e "You've created a new Ren'Py game."
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()

        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': 'start_a170b500',
            'source': 'game/script.rpy:27',
            'text': r"You've created a new Ren'Py game.",
            'translation': None
        }])

        lines = """
# game/script.rpy:64
translate pot start_130610c2:

    # nvl clear
    # nvle "You use 'nvl clear' to clear the screen when that becomes necessary."
    nvl clear
    nvle "You use 'nvl clear' to clear the screen when that becomes necessary."
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()

        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': 'start_130610c2',
            'source': 'game/script.rpy:64',
            'text': r"You use 'nvl clear' to clear the screen when that becomes necessary.",
            'translation': None
        }])

        lines = """
translate russian tutorial_nvlmode_76b2fe88:

    # nvl clear
    nvl clear
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = """
translate piglatin style default:
# comment but not the end of the bloc
    font "stonecutter.ttf"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = """
translate piglatin python:

    style.default.font = "stonecutter.ttf"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = """
translate pot strings:

    # script.rpy:14
    old "Eileen"
    new "translation1"

    # script.rpy:40
    old "string ' character"
    new "translation2"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [
            {'id':None, 'source':'script.rpy:14', 'text':"Eileen", 'translation':"translation1"},
            {'id':None, 'source':'script.rpy:40', 'text':"string ' character", 'translation':"translation2"}
        ])

        lines = """\
# game/script.rpy:27
translate pot start_a170b500:

    # e "You've created a new Ren'Py game."
    e "You've created a new Ren'Py game."

# game/script.rpy:29
translate pot start_a1247ef6:

    # "Eileen" "Once you add a story, pictures, and music, you can release it to the world!"
    "Eileen" "Once you add a story, pictures, and music, you can release it to the world!"\
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()

        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': 'start_a170b500',
            'source': 'game/script.rpy:27',
            'text': r"You've created a new Ren'Py game.",
            'translation': None
        }])
        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': 'start_a1247ef6',
            'source': 'game/script.rpy:29',
            'text': r"Once you add a story, pictures, and music, you can release it to the world!",
            'translation': None
        }])

if __name__ == '__main__':
    unittest.main()
