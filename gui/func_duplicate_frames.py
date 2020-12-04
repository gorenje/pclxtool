from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def duplicate_frames_layout():
    return [
        [sg.Text("Start Frame (Won't be duplicated)",
                 relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")],

        [sg.Checkbox('All Frames', key="all_frames", enable_events=True)],

        [sg.Text('Repeat Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="2", key="count")],

        [
            sg.Radio('Move All Elements',
                     group_id="a",
                     key="move_all_elements", default=True),
        ],[
            sg.Radio('Move Along X only',
                     group_id="a",
                     key="only_x"),
        ],[
            sg.Radio('Move Along Y Only',
                     group_id="a",
                     key="only_y"),
        ],[
            sg.Radio('No Move, Duplicate excluding start frame',
                     group_id="a",
                     key="keep_position"),
        ],[
            sg.Radio('No Move, Duplicate including Start Frame',
                     group_id="a",
                     key="duplicate_all"),
        ],

        [sg.Checkbox('Move existing frames', key="move_existing")],

    ] + ButtonsAndStatus()


def duplicate_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "all_frames":
        windw["to_frame"].Update(disabled=values["all_frames"])
        windw["from_frame"].Update(disabled=values["all_frames"])

    if event == "doit":
        windw['-status-'].Update("Duplicating Film")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.to_frame      = int(values["to_frame"])
        opts.from_frame    = int(values["from_frame"])
        opts.count         = int(values["count"])

        opts.keep_position = values["keep_position"]
        opts.duplicate_all = values["duplicate_all"]
        opts.only_x        = values["only_x"]
        opts.only_y        = values["only_y"]
        opts.move_existing = values["move_existing"]
        opts.all_frames    = values["all_frames"]
        # ignore move_all_elements since this is the default behaviour

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
