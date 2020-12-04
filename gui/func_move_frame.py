import PySimpleGUIQt as sg

from .extensions import Options
from .helpers    import *
from .icons      import coords64

def move_frames_layout():
    return [
        [
            sg.Button('', image_data=coords64)
        ],
        [
            sg.Radio('All', group_id="a",
                     key="move_xy", default=True, enable_events=True),
            sg.Radio('X Only', group_id="a",
                     key="x_only", enable_events=True),
            sg.Radio('Y Only', group_id="a",
                     key="y_only", enable_events=True),
        ],
        [
            sg.Text('X Delta', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="x_delta"),
            sg.Text('Y Delta', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="y_delta")
        ],
        [sg.Checkbox('Absolute Coordinates',
                     key="abscoords",
                     default=False,
                     enable_events=True)],
        [
            sg.Text('New Location - X', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="x_abscoords", disabled=True),
            sg.Text('New Location - Y', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="y_abscoords", disabled=True)
        ],

        [
            sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="1", key="from_frame"),

            sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="10", key="to_frame"),
            sg.Checkbox('All Frames', key="all_frames",
                        default=False, enable_events=True)
        ],

        [
            sg.Button('Ok',button_color=BlackWhite,
                      pad=(10,7), border_width=2, size=(7,1),
                   bind_return_key=True,
                      key="doit"),
            sg.VerticalSeparator(),
            sg.Button('Cancel',button_color=BlackWhite,
                      pad=(10,7), border_width=2, size=(7,1),
                      key="-close-")
        ],

        [sg.Text('', relief=sg.RELIEF_SUNKEN,
                 size=(55, 1), pad=(0, 3), key='-status-')]
    ]

def move_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event in ["abscoords", "x_only", "y_only", "move_xy"]:
        x_disabled = not (values["x_only"] or values["move_xy"])
        y_disabled = not (values["y_only"] or values["move_xy"])

        x_delta_disabled = values["abscoords"]       or x_disabled
        x_abs_disabled   = (not values["abscoords"]) or x_disabled
        y_delta_disabled = values["abscoords"]       or y_disabled
        y_abs_disabled   = (not values["abscoords"]) or y_disabled

        windw["x_delta"    ].Update(disabled=x_delta_disabled)
        windw["y_delta"    ].Update(disabled=y_delta_disabled)
        windw["x_abscoords"].Update(disabled=x_abs_disabled)
        windw["y_abscoords"].Update(disabled=y_abs_disabled)

    if event == "all_frames":
        windw["to_frame"].Update(disabled=(values["all_frames"]))
        windw["from_frame"].Update(disabled=(values["all_frames"]))

    if event == "doit":
        windw['-status-'].Update("Moving Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.x_delta     = int(values["x_delta"])
        opts.y_delta     = int(values["y_delta"])
        opts.x_abscoords = int(values["x_abscoords"])
        opts.y_abscoords = int(values["y_abscoords"])
        opts.abscoords   = values["abscoords"]
        opts.x_only      = values["x_only"]
        opts.y_only      = values["y_only"]

        opts.to_frame, opts.from_frame = None, None
        if not values["all_frames"]:
            opts.to_frame   = int(values["to_frame"])
            opts.from_frame = int(values["from_frame"])

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
