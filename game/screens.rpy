init -1  python:
    if renpy.windows:
        import EasyDialogsWin as EasyDialogs
    else:
        EasyDialogs = None

    import subprocess
    import glob
    import os
    outdir = os.path.join(config.basedir,'out')
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    def open_directory(directory):
        try:
            directory = renpy.fsencode(directory)

            if renpy.windows:
                os.startfile(directory)
            elif renpy.macintosh:
                subprocess.Popen([ "open", directory ])
            else:
                subprocess.Popen([ "xdg-open", directory ])
        except Exception, e:
            print(e)

    def projects_directory():
        f = os.path.join(renpy.config.savedir,'..','launcher-4/persistent')
        p = renpy.persistent.load(f)
        return p and p.projects_directory

    def projects_list():
        import glob
        dirs = []
        projects_dir = projects_directory()
        if projects_dir and projects_dir != config.renpy_base:
            dirs += sorted(glob.glob(os.path.join(projects_dir,'*')))
        dirs += sorted(glob.glob(os.path.join(config.renpy_base,'*')))
        return [d for d in dirs if os.path.isdir(os.path.join(d,'game'))]

    def languages_list():
        if store.projectpath is None:
            return []
        dirs = glob.glob(os.path.join(projectpath,'game','tl','*'))
        return [os.path.basename(d) for d in sorted(dirs) if os.path.isdir(d)]
        

    # The color of non-interactive text.
    TEXT = "#545454"

    # Colors for buttons in various states.
    IDLE = "#42637b"
    HOVER = "#d86b45"
    DISABLED = "#808080"

    # Colors for reversed text buttons (selected list entries).
    REVERSE_IDLE = "#78a5c5"
    REVERSE_HOVER = "#d86b45"
    REVERSE_TEXT = "#ffffff"

    # Colors for the scrollbar thumb.
    SCROLLBAR_IDLE = "#dfdfdf"
    SCROLLBAR_HOVER = "#d86b45"

    INDENT = 20

define projectpath = None
define language = None

# Recover from Python exception on "Ignore"
label start:
    call screen main_menu
    return

# label to create new context so Ren'Py doesn't complain
label ltest_error:
    $ interface.error("blah")

# Doesn't create a new context:
#    init python:
#    class test_error(Action):
#        def __call__(self):
#            interface.error("blah")
#            #call ltest_error
#            #jump start

# Action labels
# - labels rather than Action classes to create new contexts and have a chance to update the interface
# - Jump() rather than Call() because Call() doesn't Return to the calling screen (Ren'Py launcher does the same)

label TL2POT:
    if store.projectpath:
        show screen progress
        pause 0
        python hide:
            renpy.not_infinite_loop(30)
            import tl2pot
            tl2pot.tl2pot(store.projectpath,
                os.path.join(outdir, os.path.basename(store.projectpath) + '.pot'))
            open_directory(outdir)
    hide screen progress
    call screen main_menu

label TL2PO:
    if store.projectpath and store.language:
        show screen progress
        pause 0
        python hide:
            renpy.not_infinite_loop(30)
            import tl2po
            tl2po.tl2po(store.projectpath,
                store.language,
                os.path.join(outdir, os.path.basename(store.projectpath) + '-' + store.language + '.po'))
            open_directory(outdir)
    hide screen progress
    call screen main_menu

label MO2TL:
    if store.projectpath and store.language:
        $ mofile = choose_file(outdir)
        if mofile:
            show screen progress
            pause 0
            python:
                renpy.not_infinite_loop(30)
                import mo2tl
                mo2tl.mo2tl(store.projectpath,
                            mofile,
                            store.language)
                open_directory(os.path.join(store.projectpath,'game','tl',store.language))
    hide screen progress
    call screen main_menu


screen progress:
    add "#ffffff"
    text _("Calling Ren'Py to extract latest translations, please wait..."):
        align 0.5, 0.5
        color "#ff0000"

screen main_menu():
    style_prefix "main_menu"

    add gui.main_menu_background

    ## This empty frame darkens the main menu.
    hbox:
        null width 10
        vbox:
            text _("PROJECTS") style "l_label_text" size 36 yoffset 10
            null height 20
            for p in projects_list():
                textbutton os.path.basename(p) action SetVariable('projectpath',p),SetVariable('language',None)
        null width 40
        vbox:
            null height 10
            textbutton "tl2pot: generate POT template for your game" action Jump("TL2POT")
            textbutton "tl2po: extract existing Ren'Py translations to PO catalog" action Jump("TL2PO")
            textbutton "mo2tl: inject PO/MO catalog into Ren'Py translations" action Jump("MO2TL")
            #textbutton "Test" action Jump("ltest_error")
            null height 20
            if projectpath:
                text "Set language:"
            else:
                text "< Select project"

            for l in languages_list():
                textbutton l action SetVariable('language',l)

    vbox:
        xalign 1.0
        xoffset -20
        xmaximum 800
        yalign 1.0
        yoffset -20

        text "Project path: [projectpath]"
        text "Selected language: [language]"

        text "[config.name!t]":
            style "main_menu_title"

        hbox:
            xalign 1.0
            text "v[config.version]":
                style "main_menu_version"
            text " {a=https://www.beuc.net/donate/}by Beuc{/a}":
                style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")
    xalign 1.0

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5


style l_default is default:
    color TEXT
    idle_color IDLE
    hover_color HOVER
    size 18
style l_label_text is l_default:
    size 24
    xpos INDENT
    yoffset 6


style l_root is l_default:
    background "#ffffff"
    xpadding 10
    top_padding 64
    bottom_padding 128

style l_info_frame is l_default:
    ypadding 21
    xfill True
    yminimum 180
    ypos 75

style l_info_label is l_default:
    xalign 0.5
    ypos 75
    yanchor 1.0
    yoffset 12

style l_right_button is l_default:
    xalign 1.0
    ypos 600 - 128 + 12
    left_margin 8 + INDENT
    right_margin 10 + INDENT

style l_right_button_text is l_default:
    size 30


screen common:

    default complete = None
    default total = None
    default yes = None
    default no = None
    default choices = None
    default cancel = None
    default bar_value = None

    frame:
        style "l_root"

        frame:
            style_group "l_info"

            has vbox

            text message:
                text_align 0.5
                xalign 0.5
                color "#000000"

            if complete is not None:
                add SPACER

                frame:
                    style "l_progress_frame"

                    bar:
                        range total
                        value complete
                        style "l_progress_bar"

            if bar_value is not None:
                add SPACER

                frame:
                    style "l_progress_frame"

                    bar:
                        value bar_value
                        style "l_progress_bar"


            if choices:
                add SPACER

                for v, l in choices:
                    textbutton l action SetScreenVariable("selected", v)

                if selected is not None:
                    $ continue_ = Return(selected)
                else:
                    $ continue_ = None

            if submessage:
                add SPACER

                text submessage:
                    text_align 0.5
                    xalign 0.5
                    layout "subtitle"

            if yes:
                add SPACER

                hbox:
                    xalign 0.5
                    textbutton _("Yes") style "l_button" action yes
                    null width 160
                    textbutton _("No") style "l_button" action no


        label title text_color title_color style "l_info_label"

    textbutton _("Continue") action continue_ style "l_right_button"
    key "input_enter" action continue_


init python in interface:
    from store import Return, Jump
    def error(message, submessage=None, label="start", **kwargs):
        if label is None:
            action = Return(False)
        else:
            action = Jump(label)

        return renpy.call_screen("common", title=_("ERROR"), title_color='#FF0000', message=message, submessage=submessage, continue_=action, **kwargs)
