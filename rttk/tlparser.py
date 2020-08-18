#!/usr/bin/python

# Ren'Py translate blocks parser

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

from __future__ import print_function
import re

def is_empty(line):
    return bool(re.match(r'^\s*$', line))

def is_comment(line):
    return bool(re.match(r'^\s*#', line))

def is_block_start(line):
    return line.startswith('translate ')

def extract_source(comment_line):
    return comment_line.lstrip('#').strip()

def extract_dqstrings(line):
    '''
    Extract double-quoted strings from line, with their position.
    Ren'Py dialog lines are also double-quoted in translate blocks,
    but there may be other double- and single-quoted strings around.
    '''
    def skip_to_delim(pos, delim):
        while pos < len(line) and line[pos] != delim:
            if line[pos] == '\\':
                pos += 1
            pos += 1
        return pos
    def skip_paren(pos):
        while pos < len(line) and line[pos] != ')':
            if line[pos] == '(':
                pos = skip_paren(pos+1)
            elif line[pos] in (SQ, DQ):
                delim = line[pos]
                pos += 1
                pos = skip_to_delim(pos, delim)
            pos += 1
        return pos
    pos = 0
    ret = []
    SQ = "'"
    DQ = '"'
    while pos < len(line):
        if line[pos] == '(':
            # Either already _(marked) for translation, either say
            # parameters, so discarded
            pos = skip_paren(pos+1)
        elif line[pos] in (SQ, DQ):
            delim = line[pos]
            pos += 1
            start = pos
            pos = skip_to_delim(pos, delim)
            if pos >= len(line):
                raise Exception("unterminated string: " + line[start:pos] + " in line: " + line)
            if delim == DQ:
                ret.append({'start':start, 'end':pos, 'text': line[start:pos]})
        pos += 1
    return ret

def extract_dialog_string(dialog_line):
    res = extract_dqstrings(dialog_line)
    if len(res) == 0:
        return None
    if len(res) > 1:  # (who, what)
        return res[1]
    return res[0]  # (what)

def extract_base_string(dialog_line):
    res = extract_dqstrings(dialog_line)
    if len(res) == 0:
        return None
    return res[0]

def parse_next_block(lines):
    ret = []
    block_string = {'id':None, 'source':None, 'text':None, 'translation':None}
    while len(lines) > 0:
        line = lines.pop()
        if is_empty(line):
            continue
        elif is_comment(line):
            block_string['source'] = line.lstrip().lstrip('#').strip()
        elif is_block_start(line):
            block_string['id'] = line.strip(':\n').split()[2]
            if block_string['id'] in ('style', 'python'):
                # no strings, skip
                while len(lines) > 0:
                    line = lines.pop()
                    if is_empty(line):
                        continue
                    elif is_comment(line):
                        continue
                    elif not line.startswith(' '):
                        # end of block
                        lines.append(line)
                        break
            elif block_string['id'] == 'strings':
                # basic strings block
                string = {'id':None, 'source':None, 'text':None, 'translation':None}
                while len(lines) > 0:
                    line = lines.pop()
                    if is_empty(line):
                        pass
                    elif is_comment(line):
                        string['source'] = line.lstrip().lstrip('#').strip()
                    elif not line.startswith(' '):
                        # end of block
                        lines.append(line)
                        break
                    elif line.lstrip().startswith('old '):
                        string['text'] = extract_base_string(line)['text']
                    elif line.lstrip().startswith('new '):
                        string['translation'] = extract_base_string(line)['text']
                        ret.append(string)
                        string = {'id':None, 'source':None, 'text':None, 'translation':None}
                    else:
                        pass
                break
            else:
                # dialog block
                while len(lines) > 0:
                    line = lines.pop()
                    if is_empty(line):
                        continue
                    elif not line.startswith(' '):
                        # end of block
                        lines.append(line)
                        break
                    elif is_comment(line):
                        # untranslated original
                        continue
                    else:
                        # dialog body
                        s = extract_dialog_string(line)
                        if s is None:
                            continue  # not a dialog line
                        block_string['text'] = s['text']
                ret = [block_string]
                break

        else:  # Unknown
            print("Warning: format not detected:", line)
            pass
    return ret
