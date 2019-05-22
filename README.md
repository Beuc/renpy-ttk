# Ren'Py Translator ToolKit

Tools for translators working on Ren'Py games, in particular PO format import/export.

https://www.beuc.net/renpy-ttk/


## Features / benefits

Work on your Ren'Py translation using the PO format. This brings support for iterative translation:

- Translatable strings are kept in the same order as in the Ren'Py scripts, to give you context, even after an update.  You can also sort by other criteria in your PO editor if needed.

- Fuzzy matching on update, so you can e.g. update a translation after a typo fix with a single click/keystroke.

- Detect and comment out obsolete strings on update, so you don't waste time translating them.

- Ren'Py forces you to either: display empty texts when there's no translation yet; or prefill all translations using the original language but this makes it hard to see untranslated strings. Now you can have both, as untranslated strings will be empty in your .po but filled with the original language in the Ren'Py translation files.

Handle duplicates, so you can translate the same dialog line differently depending on the context.  Only duplicates get an additional context marker, so as to avoid tons of fuzzy texts when e.g. you renamed a Ren'Py label.

Up-to-date source references (file:line).

Support customized Ren'Py translations (WIP): for instance .po doesn't support splitting a translation to several Ren'Py dialogs, but if you did that in Ren'Py with a customized translation block, add a `# renpy-ttk:ignore` comment in the `translate` block before your translations.


## Install and run

### From Ren'Py (GUI)

Place this directory along with your other Ren'Py games, so it shows
up in the Ren'Py Launcher.

Generate your game's translations once using the Ren'Py launcher.

Then run `renpy-ttk` like a game: you'll be able to select the project
to translate, the language, and run the various conversions with a
single click.


## Command line

Add `renpy.sh` to your `PATH`:

`PATH=~/.../renpy-7.2.2-sdk:$PATH ./tl2pot.py ~/.../mygame/`


## Workflow with your PO editor

### Create a new `.po` translation file from `.pot` template

Run `tl2pot`, open the `.pot` template file with your PO editor and follow its instructions.

### Update an existing `.po` translation file

Run `tl2pot` again and merge the new template `.pot` file.

With gettext: `msgmerge yourgame-lang.po yourgame.pot > yourlang-lang-updated.po`

With Poedit: open old.po > Catalog > Update from POT File > game.pot

### Convert an existing Ren'Py translation to `.po`

Run `tl2po` and open the `.po` translation file.

### Import translations for default texts

Run `tl2po` on "The Question" and import the `.po` translation file.

With gettext: use it as [compendium](https://www.gnu.org/software/gettext/manual/html_node/Using-Compendia.html#Using-Compendia):

- new:       `msgmerge -C the_question.po /dev/null yourgame.pot -o yourgame-lang.po`

- update:    `msgmerge -C the_question.po --update yourgame-lang.po yourgame.pot`

- overwrite: `msgcat --use-first -o yourgame-lang-updated.po the_question.po yourgame-lang.po # + update as above`

With Poedit: use it for Translation Memory:

- Preferences > TM > Manage > Import Translation Files... > `the_question-lang.po`
- Open `yourgame-lang.po`
- Catalog > Pre-translate

Note: Poedit ignores very short strings.

### Push your translations back to Ren'Py

Compile your `.po` to `.mo`.

With gettext: `msgfmt yourgame-lang.po -o yourgame-lang.mo`

With Poedit: done automatically on saving, or File > Compile to MO...

Run `mo2tl`. This will inject the translations in your `tl/*.rpy` files. Be sure to select the right language.

Note: `mot2tl` can compile to `.mo` for you if `msgfmt` is in the
`PATH` (i.e. under GNU/Linux).


## Caveats

Do not import Ren'Py existing translations again (`tl2po`) once you've
updated it from a `.po`. This is because renpy-ttk replaces
untranslated strings with the originals (so the player won't get empty
texts), hence a double import will import original texts as
translations.  Of course you can still import new untranslated strings
as a POT template (`tl2pot`).

Ren'Py <= 7.2.2 uses inconsistent paths, which partially breaks the
strings ordering (dialogues and choices get grouped separately).  You
may apply [#1834](https://github.com/renpy/renpy/pull/1834) to fix
this.

Don't remove the `.rpyc` files from the `tl/language` directories once
you release a version of your game.  Otherwise your players will lose
their seen texts on the next update, which is a frustrating gaming
experience.  This is not specific to renpy-ttk but it's easier to
forget about it.  You can remove `.rpy` files, but just leave `.rpyc`
files around and let Ren'Py update ("recompile") them.
