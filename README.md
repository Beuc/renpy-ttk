# Ren'Py Translator ToolKit

Tools for translators working on Ren'Py games, in particular PO format import/export.

## Features

Work on your Ren'Py translation using the PO format. This brings support for iterative translation:

- Translatable strings are kept in the same order as in the Ren'Py scripts, to give you context, even after an update.  Source file information is maintained, so you can can sort with other criteria in your PO editor if needed.

- Fuzzy matching on update, so you can e.g. update a translation after a typo fix with a single click/keystroke.

- Detect and comment out obsolete strings on update, so you don't waste time translating them.

- Ren'Py forces you to either: display empty texts when there's no translation yet; or prefill all translations using the original language but this makes it hard to see untranslated strings. Now you can have both, as untranslated strings will be empty in your .po but filled with the original language in the Ren'Py translation files.

Handle duplicates, so you can translate the same dialog line differently depending on the context.  Only duplicates get an additional context marker, so as to avoid tons of fuzzy texts when e.g. you renamed a Ren'Py label.

Up-to-date source references (file:line).

Support customized Ren'Py translations (WIP): for instance .po doesn't support splitting a translation to several Ren'Py dialogs, but if you did that in Ren'Py with a customized translation block, add a `# rttk:ignore` comment in the `translate` block before your translations.


## Using with your PO editor

### Create a new .po translation file

Run tl2pot.py and open the .pot template file.

### Update an existing .po translation file

Run tl2pot.py again and merge the new template .pot file.

With gettext: `msgmerge old.po game.pot > new.po`

With Poedit: old.po > Catalog > Update from POT File > game.pot

### Convert an existing Ren'Py translation to .po

Run tl2po.py and open the .po translation file.

### Import translations for default texts

Run tl2po.py on "The Question" and import the .po translation file.

With gettext - use a [compendium](https://www.gnu.org/software/gettext/manual/html_node/Using-Compendia.html#Using-Compendia):

- new:       `msgmerge -C the_question.po /dev/null yourgame.pot > yourgame.po`

- update:    `msgmerge -C the_question.po --update yourgame.po yourgame.pot`

- overwrite: `msgcat --use-first -o yourgame-updated.po the_question.po yourgame.po # + update as above`

With Poedit (ignores very short strings):

- Open `the_question.po`
- Preferences > TM > Manage > Import Translation Files...
- Open `yourgame.po`
- Catalog > Pre-translate

### Push your translation back to Ren'Py

Compile your .po to .mo, and run mo2tl.py.  This will update the translations in your `tl/*.rpy` files.

Note: mot2tl.py can compile to .mo for you if `msgfmt` is in the PATH. 

## Running on the command line

Add `renpy.sh` to your PATH:

`PATH=~/.../renpy-7.2.2-sdk:$PATH ./tl2pot.py ~/.../mygame/`


## Caveats

Do not import Ren'Py existing translations again (tl2po) once you've
updated it from a .po. This is because RTTK replaces untranslated
strings with the originals (so the player won't get empty texts),
hence a double import will import original texts as translations.  Of
course you can still import new untranslated strings as a POT template
(tl2pot).
