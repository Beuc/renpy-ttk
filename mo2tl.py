#!/usr/bin/python

# Convert .mo compiled catalog to .rpy translation blocks and strings

# Copyright (C) 2019, 2020  Sylvain Beucler

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
import sys, os, fnmatch, io
import re
import subprocess, shutil
import tempfile
import rttk.run, rttk.tlparser, rttk.utf_8_sig, rttk.msgfmt
import gettext

# Doc: manual .mo test:
# mkdir -p $LANG/LC_MESSAGES/
# msgfmt xxx.po -o $LANG/LC_MESSAGES/game.mo
# TEXTDOMAINDIR=. gettext -s -d game "nointeract"
# TEXTDOMAINDIR=. gettext -s -d game "script_abcd1234"$'\x4'"You've created a new Ren'Py game."

UNESCAPE_CHARS = {
    'a':  '\a',
    'b':  '\b',
    'e':  '\e',
    'f':  '\f',
    'n':  '\n',
    'r':  '\r',
    't':  '\t',
    'v':  '\v',
    '\\': '\\',
    '\'': '\'',
    '"':  '\"',
    '?':  '\?',
}
ESCAPE_CHARS = {
    '\a': r'\a',
    '\b': r'\b',
    '\e': r'\e',
    '\f': r'\f',
    '\n': r'\n',
    '\r': r'\r',
    '\t': r'\t',
    '\v': r'\v',
    '\\': r'\\',
    #'\'': r'\'',
    '\"': r'\"',
    '\?': r'\?',
}
def c_unescape(s):
    r'''
    Convert Python-style string for gettext look-up
    Like str.decode('unicode_escape') but actually support unicode characters
    No support for \xXX or \0xx.
    '''
    ret = ''
    pos = 0
    while pos < len(s):
        if s[pos] == '\\' and (pos+1) < len(s) and s[pos+1] in UNESCAPE_CHARS.keys():
            ret += UNESCAPE_CHARS[s[pos+1]]
            pos += 1
        else:
            ret += s[pos]
        pos += 1
    return ret
def c_escape(s):
    '''
    Convert gettext result back to Python-style string
    Like str.encode('string_escape') but keeping non-ASCII letters as-is
    (no \xc3\xa9 everywhere)
    '''
    return ''.join([ESCAPE_CHARS.get(c, c) for c in s])

def ugettext_nometadata(translations, lookup):
    '''
    Wrapper around translations.ugettext() to avoid returning metadata
    as the translation for the empty string
    '''
    if lookup == '':
        return None
    return translations.ugettext(lookup)

def mo2tl(projectpath, mofile, renpy_target_language):
    if not re.match('^[a-z_]+$', renpy_target_language, re.IGNORECASE):
        raise Exception("Invalid language name", renpy_target_language)

    # Refresh strings
    print("Calling Ren'Py translate to get untranslated strings")
    try:
        # Ensure Ren'Py keeps the strings order (rather than append new strings)
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass
    # using --compile otherwise Ren'Py sometimes skips half of the files
    rttk.run.renpy([projectpath, 'translate', 'pot', '--compile'])
    
    # Prepare msgid:untranslated_string index
    originals = []
    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl','pot')):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Parsing  " + os.path.join(curdir,filename))
            f = io.open(os.path.join(curdir,filename), 'r', encoding='utf-8-sig')
            lines = f.readlines()
            lines.reverse()
            while len(lines) > 0:
                originals.extend(rttk.tlparser.parse_next_block(lines))

    o_blocks_index = {}
    o_basestr_index = {}
    for s in originals:
        if s['id']:
            o_blocks_index[s['id']] = s['text']
        else:
            o_basestr_index[s['text']] = s['translation']

    print("Calling Ren'Py translate to refresh " + renpy_target_language)
    rttk.run.renpy([projectpath, 'translate', renpy_target_language, '--compile'])

    # Setup gettext directory structure
    localedir = tempfile.mkdtemp()
    if not os.environ.has_key('LANG'):
        os.environ['LANG'] = 'en_US.UTF-8'
    msgdir = os.path.join(localedir,
                          os.environ['LANG'],
                          'LC_MESSAGES')
    os.makedirs(msgdir)
    dest_mofile = os.path.join(msgdir, 'game.mo')
    if mofile.endswith('.po'):
        pofile = mofile
        print(".po ->", dest_mofile)
        rttk.msgfmt.make(pofile, dest_mofile)
    else:
        shutil.copy2(mofile, dest_mofile)
    translations = gettext.translation('game', localedir)
    class NoneOnMissingTranslation:
        @staticmethod
        def ugettext(str):
            return None
    translations.add_fallback(NoneOnMissingTranslation)

    for curdir, subdirs, filenames in os.walk(os.path.join(projectpath,'game','tl',renpy_target_language)):
        for filename in fnmatch.filter(filenames, '*.rpy'):
            print("Updating  " + os.path.join(curdir,filename))
            scriptpath = os.path.join(curdir,filename)
            f_in = io.open(scriptpath, 'r', encoding='utf-8-sig')
            lines = f_in.readlines()
            lines.reverse()  # reverse so we can pop/append efficiently
            f_in.close()
        
            out = io.open(scriptpath, 'w', encoding='utf-8-sig')
            last_comment = ''
            while len(lines) > 0:
                line = lines.pop()
                if rttk.tlparser.is_empty(line):
                    out.write(line)
                elif rttk.tlparser.is_comment(line):
                    last_comment = line
                    out.write(line)
                elif rttk.tlparser.is_block_start(line):
                    msgid = line.strip(':\n').split()[2]
                    if msgid == 'strings':
                        # basic strings block
                        out.write(line)
                        s = None
                        translation = ''
                        msgctxt = ''
                        while len(lines) > 0:
                            line = lines.pop()
                            if rttk.tlparser.is_empty(line):
                                pass
                            elif rttk.tlparser.is_comment(line):
                                msgctxt = line.lstrip().lstrip('#').strip()
                            elif not line.startswith(' '):
                                # end of block
                                lines.append(line)
                                break
                            elif line.lstrip().startswith('old '):
                                msgstr = rttk.tlparser.extract_base_string(line)['text']
                                lookup = c_unescape(msgstr)
                                lookup = msgctxt+'\x04'+lookup
                                translation = ugettext_nometadata(translations, lookup)
                                if translation is None:
                                        # no match with context, try without
                                        lookup = c_unescape(msgstr)
                                        translation = ugettext_nometadata(translations, lookup)
                                if translation is not None:
                                    translation = c_escape(translation)
                                msgctxt = ''
                            elif line.lstrip().startswith('new '):
                                if translation is not None:
                                    s = rttk.tlparser.extract_base_string(line)
                                    line = line[:s['start']]+translation+line[s['end']:]
                                translation = None
                            else:
                                # unknown
                                pass
                            out.write(line)
                    else:
                        # dialog block
                        if not o_blocks_index.has_key(msgid):
                            obsolete = u"# OBSOLETE\n"
                            if last_comment != obsolete:
                                out.write(obsolete)
                        out.write(line)
                        while len(lines) > 0:
                            line = lines.pop()
                            if rttk.tlparser.is_empty(line):
                                pass
                            elif not line.startswith(' '):
                                # end of block
                                lines.append(line)
                                break
                            elif rttk.tlparser.is_comment(line):
                                # untranslated original
                                pass
                            else:
                                # statement
                                s = rttk.tlparser.extract_dialog_string(line)
                                if s is None:
                                    # no ID (e.g. python block)
                                    pass
                                elif s['text'] is None:
                                    # no double-quoted string (e.g. nvl)
                                    pass
                                elif re.match('^\s*voice\s', line):
                                    # voice tag, not a dialog line
                                    pass
                                elif o_blocks_index.get(msgid, None) is None:
                                    # obsolete translate block, don't translate
                                    pass
                                else:
                                    msgstr = o_blocks_index[msgid]
                                    msgctxt = msgid
                                    lookup = c_unescape(msgstr)
                                    lookup = msgctxt+'\x04'+lookup
                                    translation = ugettext_nometadata(translations, lookup)
                                    if translation is None:
                                        # no match with context, try without
                                        lookup = c_unescape(msgstr)
                                        translation = ugettext_nometadata(translations, lookup)
                                    if translation is not None:
                                        translation = c_escape(translation)
                                        line = line[:s['start']]+translation+line[s['end']:]
                            out.write(line)
                # Unknown
                else:
                    print("Warning: format not detected:", line)
                    out.write(line)
    shutil.rmtree(localedir)

    try:
        # Clean-up
        shutil.rmtree(os.path.join(projectpath,'game','tl','pot'))
    except OSError:
        pass

if __name__ == '__main__':
    mo2tl(sys.argv[1], sys.argv[2], sys.argv[3])
