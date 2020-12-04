from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def delete_frames_layout():
    return [
        [sg.Text('Delete frames and either by replacing the image with an \n'+
                 'image or completely removing the frame from the layer.\n')
        ],

        [sg.Checkbox('All Frames', key="all_frames", enable_events=True)],

        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],
        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")
        ],

        [
            sg.Radio('Delete Frames',
                     group_id="a",
                     key="delete_frames", default=True),
        ],[
            sg.Radio('Replace with Empty Image',
                     group_id="a",
                     key="empty_image"),
        ],
    ] + ButtonsAndStatus()

def delete_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "all_frames":
        windw["to_frame"].Update(disabled=values["all_frames"])
        windw["from_frame"].Update(disabled=values["all_frames"])

    if event == "doit":
        windw['-status-'].Update("Deleting frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.to_frame = None
        if values["to_frame"] != "":
            opts.to_frame = int(values["to_frame"])

        opts.from_frame = None
        if values["from_frame"] != "":
            opts.from_frame = int(values["from_frame"])

        opts.delete_frames = values["delete_frames"]
        opts.empty_image   = values["delete_frames"]
        opts.all_frames    = values["all_frames"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
