# Call the scripts with the Ren'Py (limited) Python environment
# ~/.../renpy-7.2.2-sdk/renpy.sh ~/.../renpy-ttk tl2pot ...
init python:
    def version():
        renpy.arguments.takes_no_arguments("version")
        print(config.name, config.version)
        return False
    renpy.arguments.register_command("version", version)

    def tl2pot():
        ap = renpy.arguments.ArgumentParser(description="tl2pot", require_command=False)
        args, rest = ap.parse_known_args()
        import tl2pot
        tl2pot.tl2pot(*rest)
        return False
    renpy.arguments.register_command("tl2pot", tl2pot)

    def tl2po():
        ap = renpy.arguments.ArgumentParser(description="tl2po", require_command=False)
        args, rest = ap.parse_known_args()
        import tl2po
        tl2po.tl2po(*rest)
        return False
    renpy.arguments.register_command("tl2po", tl2po)

    def mo2tl():
        ap = renpy.arguments.ArgumentParser(description="mo2tl", require_command=False)
        args, rest = ap.parse_known_args()
        import mo2tl
        mo2tl.mo2tl(*rest)
        return False
    renpy.arguments.register_command("mo2tl", mo2tl)
