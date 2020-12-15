from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def scale_frames_layout():
    return [
        [sg.Text('Scale an image by percent. Scale step is additive and\n'+
                 'is increment which each frame. If duplicate is checked,\n'+
                 'then to frame is ignoreed and count number of from-frames\n'+
                 'are created and then scaled. If scaling by constant is \n'+
                 'selected, then that scaling factor will be used for all \n'+
                 'frames.\n')
        ],
        [sg.Checkbox('All Frames', key="all_frames",
                     default=False,
                     enable_events=True)],

        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")],

        [sg.Checkbox('Constant Scaling', key="scale_constant",
                     default=False,
                     enable_events=True)],

        [sg.Text('Scale Factor', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1.0", key="scale_step")],

        [sg.Text('Scale Start', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="100", key="scale_start")],

        [sg.Checkbox('Duplicate Start Frame', key="duplicate",
                     default=False,
                     enable_events=True)],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10",
                      key="count",
                      disabled=True)],
        [sg.Checkbox('Center after Scaling',
                     key="center_after_scaling",
                     default=False,
                     disabled=True)],
    ] + ButtonsAndStatus()


def scale_frames_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "all_frames":
        windw["duplicate" ].Update(disabled=values["all_frames"])
        windw["to_frame"  ].Update(disabled=values["all_frames"])
        windw["from_frame"].Update(disabled=values["all_frames"])

    if event == "duplicate":
        windw["all_frames"          ].Update(disabled=values["duplicate"])
        windw["to_frame"            ].Update(disabled=values["duplicate"])
        windw["count"               ].Update(disabled=(not values["duplicate"]))
        windw["center_after_scaling"].Update(disabled=(not values["duplicate"]))

    if event == "scale_constant":
        windw["scale_start"].Update(disabled=values["scale_constant"])

    if event == "doit":
        windw['-status-'].Update("Scaling Frames")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.to_frame             = int(values["to_frame"])
        opts.from_frame           = int(values["from_frame"])
        opts.count                = int(values["count"])
        opts.duplicate            = values["duplicate"]
        opts.scale_step           = float(values["scale_step"])
        opts.scale_start          = float(values["scale_start"])
        opts.scale_constant       = values["scale_constant"]
        opts.center_after_scaling = values["center_after_scaling"]

        opts.to_frame, opts.from_frame = None, None
        if not values["all_frames"]:
            opts.to_frame   = int(values["to_frame"])
            opts.from_frame = int(values["from_frame"])

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
