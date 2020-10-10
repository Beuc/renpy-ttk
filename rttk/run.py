#!/usr/bin/python

# Run CLI Ren'Py

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

import sys, subprocess

try:
    import renpy
    in_renpy = True
except:
    in_renpy = False

def renpy(args):
    global in_renpy
    command = ['renpy.sh']
    if in_renpy:
        # cf. launcher/game/project.rpy
        command = [sys.executable, '-EO', sys.argv[0]]
    try:
        subprocess.check_output(command+args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise Exception("Ren'Py error: " + e.output)
