from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def duplicate_layers_layout():
    return [
        [
            sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="2", key="count")
        ],
    ] + ButtonsAndStatus()


def duplicate_layers_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "doit":
        windw['-status-'].Update("Duplicating Layers")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.count  = int(values["count"])

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
