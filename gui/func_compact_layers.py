from .extensions import Options
from .helpers    import *
from .layouts    import sg, ButtonsAndStatus

def compact_layers_layout():
    return [
        [sg.Text("This removes all missing frames from a layer and moves all\n"+
                 "existing frames up until the layer is filled out. This \n"+
                 "won't remove frames have transparent or empty images.")
        ],
    ] + ButtonsAndStatus()

def compact_layers_event_handler(glbls, subwindows, window_name, target):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "doit":
        windw['-status-'].Update("Compact Layers")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        throw_off_to_thread(glbls, subwindows["info"], windw, opts, target)
