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
        self.assertTrue(tlparser.is_empty(u''))
        self.assertTrue(tlparser.is_empty(u'\n'))
        self.assertFalse(tlparser.is_empty(u'translate french start_a170b500\n'))
        self.assertFalse(tlparser.is_empty(u'# game/script.rpy:27'))

    def test_is_comment(self):
        self.assertTrue(tlparser.is_comment(u'#'))
        self.assertTrue(tlparser.is_comment(u'# game/script.rpy:27\n'))
        self.assertFalse(tlparser.is_comment(u' '))
        self.assertFalse(tlparser.is_comment(u'e "Hello"'))
        self.assertFalse(tlparser.is_comment(u'translate french start_a170b500  # test\n'))

    def test_is_block_start(self):
        self.assertTrue(tlparser.is_block_start(u'translate french start_a170b500  # test\n'))
    def test_extract_source(self):
        self.assertEqual(tlparser.extract_source(u'# game/script.rpy:27\n'), u'game/script.rpy:27')

    def test_extract_dqstrings(self):
        testcase = ur'''    _( 'string " character' ) "Tricky single/double '\" multiple strings 2"'''
        self.assertEqual(tlparser.extract_dqstrings(testcase),
            [{'start': 31, 'end': 74, 'text': ur'''Tricky single/double '\" multiple strings 2'''}])
        testcase = ur'''_( "string \" character" ) "Tricky double/double \"' multiple strings"'''
        self.assertEqual(tlparser.extract_dqstrings(testcase),
            [{'start':  4, 'end': 23, 'text': ur'''string \" character'''},
             {'start': 28, 'end': 69, 'text': ur'''Tricky double/double \"' multiple strings'''}])

    def test_extract_base_string(self):
        self.assertEqual(
            tlparser.extract_base_string(u'''    old "menu title"\n'''),
            {'start': 9, 'end': 19, 'text': u'menu title'})

    def test_extract_dialog_string(self):
        self.assertEqual(
            tlparser.extract_dialog_string(u'''e "You've created a new Ren'Py game."\n'''),
            {'start': 3, 'end': 36, 'text': u"You've created a new Ren'Py game."})
        testcase = ur'''    _( 'string " character' ) "Tricky single/double '\" multiple strings 2"'''
        self.assertEqual(tlparser.extract_dialog_string(testcase),
            {'start': 31, 'end': 74, 'text': ur'''Tricky single/double '\" multiple strings 2'''})

    def test_parse_next_block(self):
        # https://www.renpy.org/doc/html/translation.html
        lines = u"""
# TODO: Translation updated at 2019-05-18 19:13

# game/script.rpy:27
translate pot start_a170b500:

    # e "You've created a new Ren'Py game."
    e "You've created a new Ren'Py game."
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()

        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': u'start_a170b500',
            'source': u'game/script.rpy:27',
            'text': ur"You've created a new Ren'Py game.",
            'translation': None
        }])

        lines = u"""
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
            'id': u'start_130610c2',
            'source': u'game/script.rpy:64',
            'text': ur"You use 'nvl clear' to clear the screen when that becomes necessary.",
            'translation': None
        }])

        lines = u"""
translate russian tutorial_nvlmode_76b2fe88:

    # nvl clear
    nvl clear
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = u"""
translate piglatin style default:
# comment but not the end of the bloc
    font "stonecutter.ttf"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = u"""
translate piglatin python:

    style.default.font = "stonecutter.ttf"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()
        self.assertEqual(tlparser.parse_next_block(lines), [])

        lines = u"""
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
            {'id':None, 'source':u'script.rpy:14', 'text':u"Eileen", 'translation':u"translation1"},
            {'id':None, 'source':u'script.rpy:40', 'text':u"string ' character", 'translation':u"translation2"}
        ])

        lines = u"""\
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
            'id': u'start_a170b500',
            'source': u'game/script.rpy:27',
            'text': ur"You've created a new Ren'Py game.",
            'translation': None
        }])
        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': u'start_a1247ef6',
            'source': u'game/script.rpy:29',
            'text': ur"Once you add a story, pictures, and music, you can release it to the world!",
            'translation': None
        }])

        lines = u"""\
# game/script.rpy:92
translate french start_06194c6b:

    # voice "path/to/file"
    # e "voiced text"
    voice "path/to/file"
    e "voiced text"
"""
        lines = [l+"\n" for l in lines.split("\n")]
        lines.reverse()

        self.assertEqual(tlparser.parse_next_block(lines), [{
            'id': u'start_06194c6b',
            'source': u'game/script.rpy:92',
            'text': ur"voiced text",
            'translation': None
        }])

if __name__ == '__main__':
    unittest.main()
