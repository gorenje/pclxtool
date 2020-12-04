from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def reverse_frames_layout():
    return [
        [
            sg.Checkbox('Reverse All Frames', key="all_frames",
                        default=True, enable_events=True)
        ],
        [
            sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="1", key="from_frame", disabled=True)
        ],
        [
            sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="10", key="to_frame", disabled=True)
        ],
    ] + ButtonsAndStatus()

def reverse_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "all_frames":
        windw["to_frame"].Update(disabled=values["all_frames"])
        windw["from_frame"].Update(disabled=values["all_frames"])

    if event == "doit":
        windw['-status-'].Update("Reversing Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.to_frame = None
        if values["to_frame"] != "":
            opts.to_frame = int(values["to_frame"])

        opts.from_frame = None
        if values["from_frame"] != "":
            opts.from_frame = int(values["from_frame"])

        opts.all_frames = values["all_frames"]

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
