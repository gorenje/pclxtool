from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def gradient_background_layout(pclx_infos):
    cvinfos = pclx_infos["cv"][list(pclx_infos["cv"].keys())[0]]

    return [
        [sg.Text("Start Frame",
                 relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="count")],


        [sg.Text('Start Color (#rrggbb)', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="#ffffff", key="start_color")],

        [sg.Text('End Color (#rrggbb)', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="#000000", key="end_color")],

        [sg.Text('Width', relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text=cvinfos["width"], key="width")
        ],

        [sg.Text('Height', relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text=cvinfos["height"], key="height")
        ],
    ] + ButtonsAndStatus()

def gradient_background_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "doit":
        windw['-status-'].Update("Gradient Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.from_frame  = int(values["from_frame"])
        opts.count       = int(values["count"])
        opts.height      = int(values["height"])
        opts.width       = int(values["width"])
        opts.start_color = values["start_color"]
        opts.end_color   = values["end_color"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
