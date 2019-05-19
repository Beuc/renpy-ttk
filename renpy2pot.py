#!/usr/bin/python

# Convert .rpy translation blocks to .pot gettext template

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

# PATH=~/.../renpy-7.2.2-sdk:$PATH ./i18n_renpy2pot.py ~/.../mygame/
# msgmerge old.po game.pot > new.po
# Or Poedit old.po > Catalog > Update from POT File > game.pot

from __future__ import print_function
import sys, os, fnmatch
import re
import subprocess, shutil

def is_empty(line):
    return bool(re.match(r'^\s*$', line))

def is_comment(line):
    return bool(re.match(r'^\s*#', line))

def is_block_start(line):
    return line.startswith('translate ')

def extract_source(comment_line):
    return comment_line.lstrip('#').strip()

def extract_dqstrings(line):
    '''Extract double-quoted strings from line'''
    def skip_to_delim(pos, delim):
        while pos < len(line) and line[pos] != delim:
            if line[pos] == '\\':
                pos += 1
            pos += 1
        return pos
    pos = 0
    ret = []
    SQ = "'"
    DQ = '"'
    while pos < len(line):
        if line[pos] in (SQ, DQ):
            delim = line[pos]
            pos += 1
            start = pos
            pos = skip_to_delim(pos, delim)
            if pos >= len(line) or line[pos] != delim:
                raise Exception("unterminated string: " + line[start:pos])
            if delim == DQ:
                ret.append(line[start:pos])
        pos += 1
    return ret

def extract_dialog_string(dialog_line):
    res = extract_dqstrings(dialog_line)
    if len(res) == 0:
        return None
    if len(res) > 1:  # (who, what)
        return res[1]
    return res[0]  # (what)

def parse_next_block(lines):
    ret = []
    block_string = {'id':None, 'source':None, 'text':None}
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
                pass
            elif block_string['id'] == 'strings':
                # basic strings block
                string = {'id':None, 'source':None, 'text':None}
                while len(lines) > 0:
                    line = lines.pop()
                    if is_empty(line):
                        pass
                    elif not line.startswith(' '):
                        # end of block
                        lines.append(line)
                        break
                    elif is_comment(line):
                        string['source'] = line.lstrip().lstrip('#').strip()
                    elif line.lstrip().startswith('old '):
                        string['text'] = line.strip().lstrip('old "').rstrip('"')
                        ret.append(string)
                        string = {'id':None, 'source':None, 'text':None}
                    else:
                        pass
                break
            else:
                # dialog block
                while len(lines) > 0:
                    line = lines.pop()
                    if is_empty(line):
                        pass
                    elif not line.startswith(' '):
                        # end of block
                        lines.append(line)
                        break
                    elif is_comment(line):
                        # untranslated original
                        pass
                    else:
                        # dialog body
                        s = extract_dialog_string(line)
                        if s is None:
                            pass  # not a dialog line
                        block_string['text'] = s
                ret = [block_string]
                break

        else:  # Unknown
            pass
    return ret

def convert(projectpath):
    # Refresh strings
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass
    # TODO: renpy within renpy == sys.executable -EO sys.argv[0]
    # cf. launcher/game/project.rpy
    print("Calling Ren'Py translate")
    # using --compile otherwise Ren'Py sometimes skips half of the files
    ret = subprocess.call(['renpy.sh', projectpath, 'translate', 'pot', '--compile'])
    if ret != 0:
        print("Ren'Py error")
        sys.exit(1)
    
    print("Generating game.pot...")
    strings = []
    out = open('game.pot', 'w')
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl','pot')):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = open(os.path.join(curdir,filename), 'r')
            lines = f.readlines()
            lines[0].lstrip('\ufeff')  # BOM

            lines.reverse()
            while len(lines) > 0:
                strings.extend(parse_next_block(lines))
    
    occurrences = {}
    for s in strings:
        occurrences[s['text']] = occurrences.get(s['text'], 0) + 1

    for s in strings:
        if occurrences[s['text']] > 1:
            out.write('msgctxt "' + s['id'] + '"\n')
        out.write('#: ' + s['source'] + '\n')
        out.write('msgid "' + s['text'] + '"\n')
        out.write('msgstr ""\n')
        out.write('\n')

if __name__ == '__main__':
    convert(sys.argv[1])
