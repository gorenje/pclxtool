import PySimpleGUIQt as sg

from .extensions import Options
from .helpers    import *

def rotate_layout():
    return [
        [sg.Text(
            'Rotate frames by degrees. If you want to rotate an image\n'+
            'about its center, without cropping, then extend its canvas\n'+
            'beforehand.\n'
        )],

        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="to_frame")
        ],

        [sg.Checkbox('Constant Rotating', key="rotate_constant",
                     default=False,
                     enable_events=True)],

        [sg.Text('Rotate Step', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1.5", key="rotate_step")
        ],

        [sg.Text('Rotate Start', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="0", key="rotate_start")
        ],

        [sg.Checkbox('Extend canvas before rotation',
                     key="extend_frames", default=False, enable_events=True)
        ],
        [
            sg.Text('Extend To', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="0",
                         key="extent_x",
                         enable_events=True,
                         disabled=True),
            sg.Text(',', size=(2, 1), pad=(0, 1)),
            sg.InputText(default_text="0", key="extent_y",disabled=True)
        ],

        [
            sg.Checkbox('Duplicate Frames', key="duplicate",
                        default=False,
                        enable_events=True)
        ],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="count", disabled=True)
        ],

        [sg.Button('Ok',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   bind_return_key=True,
                   key="doit"),
         sg.VerticalSeparator(),
         sg.Button('Cancel',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   key="-close-")],
        [sg.Text('', relief=sg.RELIEF_SUNKEN,
                 size=(40, 1), pad=(0, 3), key='-status-')]
    ]

def rotate_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "extent_x":
        windw["extent_y"].Update(values["extent_x"])

    if event == "duplicate":
        windw["to_frame"].Update(disabled=values["duplicate"])
        windw["count"].Update(disabled=(not values["duplicate"]))

    if event == "rotate_constant":
        windw["rotate_start"].Update(disabled=values["rotate_constant"])

    if event == "extend_frames":
        windw["extent_x"].Update(disabled=(not values["extend_frames"]))
        windw["extent_y"].Update(disabled=(not values["extend_frames"]))

    if event == "doit":
        windw['-status-'].Update("Rotating and Duplicating Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.from_frame      = int(values["from_frame"])
        opts.to_frame        = int(values["to_frame"])
        opts.rotate_step     = float(values["rotate_step"])
        opts.rotate_start    = float(values["rotate_start"])
        opts.count           = int(values["count"])
        opts.extent_x        = int(values["extent_x"])
        opts.extent_y        = int(values["extent_y"])
        opts.extend_frames   = values["extend_frames"]
        opts.rotate_constant = values["rotate_constant"]
        opts.duplicate       = values["duplicate"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
