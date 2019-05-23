init offset = -2
init python:
    gui.init(800, 600)

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    underline True
    hover_underline False

style gui_text:
    properties gui.text_properties("interface")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


define gui.main_menu_background = '#f0f0f0'

define gui.accent_color = '#000066'
define gui.idle_color = '#222222'
define gui.idle_small_color = '#888888'
define gui.hover_color = '#3333CC'
define gui.selected_color = '#555555'
define gui.insensitive_color = '#aaaaaa7f'

define gui.text_font = "DejaVuSans.ttf"
define gui.name_text_font = "DejaVuSans.ttf"
define gui.interface_text_font = "DejaVuSans.ttf"
define gui.text_size = 22
define gui.name_text_size = 30
define gui.interface_text_size = 18
define gui.label_text_size = 24
define gui.notify_text_size = 16
define gui.title_text_size = 50

define gui.button_width = None
define gui.button_height = None
define gui.button_borders = Borders(4, 4, 4, 4)
define gui.button_tile = False
define gui.button_text_font = gui.interface_text_font
define gui.button_text_size = gui.interface_text_size
define gui.button_text_idle_color = gui.idle_color
define gui.button_text_hover_color = gui.hover_color
define gui.button_text_selected_color = gui.selected_color
define gui.button_text_insensitive_color = gui.insensitive_color
define gui.button_text_xalign = 0.0

define gui.frame_borders = Borders(4, 4, 4, 4)
define gui.confirm_frame_borders = Borders(40, 40, 40, 40)
define gui.skip_frame_borders = Borders(16, 5, 50, 5)
define gui.notify_frame_borders = Borders(16, 5, 40, 5)
define gui.frame_tile = False

define gui.bar_size = 25
define gui.scrollbar_size = 12
define gui.slider_size = 25
define gui.bar_tile = False
define gui.scrollbar_tile = False
define gui.slider_tile = False
define gui.bar_borders = Borders(4, 4, 4, 4)
define gui.scrollbar_borders = Borders(4, 4, 4, 4)
define gui.slider_borders = Borders(4, 4, 4, 4)
define gui.vbar_borders = Borders(4, 4, 4, 4)
define gui.vscrollbar_borders = Borders(4, 4, 4, 4)
define gui.vslider_borders = Borders(4, 4, 4, 4)
define gui.unscrollable = "hide"

define gui.language = "unicode"
