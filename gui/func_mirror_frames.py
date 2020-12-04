from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def mirror_frames_layout():
    return [
        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")
        ],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")
        ],

        [sg.Checkbox('All Frames',
                     default=False,
                     key="all_frames",
                     enable_events=True)],

        [
            sg.Radio('Vertical Flip', group_id="a",
                     key="vertical_flip", default=True),
        ],[
            sg.Radio('Horizonal Flip', group_id="a",
                     key="horizontal_flip"),
        ],
    ] + ButtonsAndStatus()

def mirror_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "all_frames":
        windw["to_frame"].Update(disabled=values["all_frames"])
        windw["from_frame"].Update(disabled=values["all_frames"])

    if event == "doit":
        windw['-status-'].Update("Mirror Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.from_frame      = int(values["from_frame"])
        opts.to_frame        = int(values["to_frame"])
        opts.vertical_flip   = values["vertical_flip"]
        opts.horizontal_flip = values["horizontal_flip"]
        opts.all_frames      = values["all_frames"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
