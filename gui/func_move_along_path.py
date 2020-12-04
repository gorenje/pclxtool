import PySimpleGUIQt as sg

from .extensions import Options
from .helpers    import *

def move_along_path_layout():
    return [
        [
            sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="1", key="from_frame")],
        [
            sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="10", key="to_frame")
        ],

        [
            sg.InputText(default_text='',
                         key='FILENAME',
                         size=(20, 1),
                         enable_events=True),
            sg.Button('Browse', size=(7,1),
                      button_color=BlackWhite,
                      enable_events=True,
                      key="browse")
        ],

        [
            sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="10",
                         key="count",
                         disabled=True)
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
                 size=(55, 1), pad=(0, 3), key='-status-')]
    ]

def move_along_path_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "FILENAME":
        if os.path.isfile(values["FILENAME"].replace("file://","")):
            windw["to_frame"].Update(disabled=True)
            windw["count"].Update(disabled=False)

    if event == "browse":
        windw["browse"].Update(disabled=True)
        filename = sg.PopupGetFile("Find SVG",
                                   file_types=(("SVGs","*.svg"),))
        if filename: windw['FILENAME'].Update(filename)
        windw["browse"].Update(disabled=False)

    if event == "doit":
        windw['-status-'].Update("Moving objects along path")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.from_frame   = int(values["from_frame"])
        opts.to_frame     = int(values["to_frame"])
        opts.count        = int(values["count"])
        opts.svg_filename = values["FILENAME"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
