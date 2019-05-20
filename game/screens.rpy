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

    class TL2POT(Action):
        def __call__(self):
            if store.projectpath:
                import tl2pot
                tl2pot.tl2pot(store.projectpath,
                    os.path.join(outdir, os.path.basename(store.projectpath) + '.pot'))
                open_directory(outdir)

    class TL2PO(Action):
        def __call__(self):
            if store.projectpath and store.language:
                import tl2po
                tl2po.tl2po(store.projectpath,
                    store.language,
                    os.path.join(outdir, os.path.basename(store.projectpath) + '-' + store.language + '.po'))
                open_directory(outdir)

    class MO2TL(Action):
        def __call__(self):
            if store.projectpath and store.language:
                mofile = choose_file(outdir)
                if mofile:
                    import mo2tl
                    mo2tl.mo2tl(store.projectpath,
                                mofile,
                                store.language)
                    open_directory(os.path.join(store.projectpath,'game','tl',store.language))

    def projects_directory():
        f = os.path.join(renpy.config.savedir,'..','launcher-4/persistent')
        p = renpy.persistent.load(f)
        return p.projects_directory

    def projects_list():
        import glob
        dirs = (
            sorted(glob.glob(os.path.join(projects_directory(),'*'))) +
            sorted(glob.glob(os.path.join(config.renpy_base,'*')))
        )
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

screen main_menu():
    style_prefix "main_menu"

    add gui.main_menu_background

    ## This empty frame darkens the main menu.
    hbox:
        null width 10
        vbox:
            text _("PROJECTS:") style "l_label_text" size 36 yoffset 10
            null height 20
            for p in projects_list():
                textbutton os.path.basename(p) action SetVariable('projectpath',p),SetVariable('language',None)
        null width 20
        vbox:
            null height 10
            textbutton "Generate POT template (tl2pot)" action TL2POT()
            textbutton "Convert Ren'Py translations to PO catalog (tl2po)" action TL2PO()
            textbutton "Update Ren'Py translation from MO catalog (mo2tl)" action MO2TL()
            null height 20
            text "Set language:":
                color "#000000"
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
