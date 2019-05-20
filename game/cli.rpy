# In case we need to call Ren'Py functions, we still can support CLI though e.g.
# ~/.../renpy-7.2.2-sdk/renpy.sh ~/.../renpy-ttk tl2pot
init python:
    def tl2pot():
        renpy.arguments.takes_no_arguments("tl2pot")
        print("tl2pot")
        import sys
        import tl2pot
        # TODO
        return False
    renpy.arguments.register_command("tl2pot", tl2pot)
