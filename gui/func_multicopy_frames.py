import PySimpleGUIQt as sg

from .extensions import Options
from .helpers    import *

def multicopy_frames_layout():
    return [
        [sg.Text("Start Frame",
                 relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="2", key="count")],

        [sg.Button('Ok',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   bind_return_key=True,
                   key="doit"),
         sg.VerticalSeparator(),
         sg.Button('Cancel',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   key="-close-")],
        [sg.Text('', relief=sg.RELIEF_SUNKEN,
                 size=(55, 1), pad=(0, 3), key='-status-')]
    ]

def multicopy_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "doit":
        windw['-status-'].Update("Copying Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.to_frame   = int(values["to_frame"])
        opts.from_frame = int(values["from_frame"])
        opts.count      = int(values["count"])

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
