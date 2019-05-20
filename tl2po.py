#!/usr/bin/python

# Convert .rpy translation blocks and strings to .po gettext catalog

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

# Use cases:
# - import your game's translation started in Ren'Py format
# - import default Ren'Py translated strings from "The Question"

from __future__ import print_function
import sys, os, fnmatch
import re
import shutil
import tlparser, tlrun


def tl2po(projectpath, language, outfile=None):
    if not re.match('^[a-z_]+$', language):
        raise Exception("Invalid language", language)
    if not os.path.isdir(os.path.join(projectpath,'game','tl',language)):
        raise Exception("Language not found", os.path.join(projectpath,'game','tl',language))

    if outfile is None:
        outfile = language+'.po'

    # Refresh strings
    print("Calling Ren'Py translate")
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass
    # using --compile otherwise Ren'Py sometimes skips half of the files
    tlrun.renpy([projectpath, 'translate', 'pot', '--compile'])
    
    originals = []
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl','pot')):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = open(os.path.join(curdir,filename), 'r')
            lines = f.readlines()
            if lines[0].startswith('\xef\xbb\xbf'):
                lines[0] = lines[0][3:]  # BOM

            lines.reverse()
            while len(lines) > 0:
                originals.extend(tlparser.parse_next_block(lines))

    translated = []
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl',language)):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = open(os.path.join(curdir,filename), 'r')
            lines = f.readlines()
            if lines[0].startswith('\xef\xbb\xbf'):
                lines[0] = lines[0][3:]  # BOM

            lines.reverse()
            while len(lines) > 0:
                translated.extend(tlparser.parse_next_block(lines))

    t_blocks_index = {}
    t_basestr_index = {}
    for s in translated:
        if s['id']:
            t_blocks_index[s['id']] = s['text']
        else:
            t_basestr_index[s['text']] = s['translation']
    
    occurrences = {}
    for s in originals:
        occurrences[s['text']] = occurrences.get(s['text'], 0) + 1

    out = open(outfile, 'w')
    out.write(r"""msgid ""
msgstr ""
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

""")
    for s in originals:
        out.write('#: ' + s['source'] + '\n')
        if occurrences[s['text']] > 1:
            out.write('msgctxt "' + (s['id'] or s['source']) + '"\n')
        out.write('msgid "' + s['text'] + '"\n')
        if s['id'] is not None and t_blocks_index.has_key(s['id']):
            out.write('msgstr "' + t_blocks_index[s['id']] + '"\n')
        else:
            out.write('msgstr "' + t_basestr_index.get(s['text'],'') + '"\n')
        out.write('\n')
    print("Wrote '" + outfile + "'.")

    try:
        # Clean-up
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass

if __name__ == '__main__':
    tl2po(sys.argv[1], sys.argv[2])
