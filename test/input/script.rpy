# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
define nvle = Character(_("Eileen"), color="#c8ffc8", kind=nvl)

# The game starts here.

label start:

    # Show a background. This uses a placeholder by default, but you can
    # add a file (named either "bg room.png" or "bg room.jpg") to the
    # images directory to show it.

    scene bg room

    # This shows a character sprite. A placeholder is used, but you can
    # replace it by adding a file named "eileen happy.png" to the images
    # directory.

    show eileen happy

    # These display lines of dialogue.

    e "You've created a new Ren'Py game."

    "Eileen" "Once you add a story, pictures, and music, you can release it to the world!"

    "Eileen" "Once you add a story, pictures, and music, you can release it to the world!"  # dup

    _("string ' character") "Multiple strings"

    _( "string ' character" ) "Tricky double-quoted \"' multiple strings"

    _( 'string " character' ) 'Tricky single-quoted "\' multiple strings'

    _( 'string \' character' ) "Tricky single/double \"' multiple strings 1"

    _( 'string " character' ) "Tricky single/double '\" multiple strings 2"

    _( "string \" character" ) "Tricky double/double \"' multiple strings"

    _("string character") "inline transition" with vpunch

    e "nointeract" nointeract

    "Implicit narrator"

    'single-quoted " string'

    e 'single-quoted " string'

    # no-dialog translate block:
    nvl clear
    nvl show dissolve

    nvle "Then just use that character in a say statement."

    nvl clear

    nvle "You use 'nvl clear' to clear the screen when that becomes necessary."

    e '''
multiline
triple-quoted
dialog
entry
without
newlines
'''

    e """
Roses are red\n
Violet are blue\n
Regexs are   hard\n
Except for you?
"""

    e """multiline\ndialog\nentry\nwith\nnewlines"""

    _("multiline\ncharacter") "Not translated"

    menu:
        "dupmenutitle"
        "dupmenuentry":
            pass
        "dupmenuentry":
            pass

    voice "path/to/file"
    e "voiced text"

    call dup

    return
