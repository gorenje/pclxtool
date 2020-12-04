import PySimpleGUIQt as sg

from .extensions import Options
from .helpers    import *

def make_movie_layout(pclx_infos, ffmpeg_profiles, prores_profiles):
    ## TODO support multiple camera views by providing a dropdown with
    ## TODO all available camera views.
    cvinfos = pclx_infos["cv"][list(pclx_infos["cv"].keys())[0]]

    return [
        [sg.Text('Encoding Profile',
                 relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.Combo([""]+list(ffmpeg_profiles.keys()),
                  auto_size_text=True,
                  size=(200,20),
                  key="encoding_profile",
                  default_value="",
                  enable_events=True)
        ],
        [
            sg.HorizontalSeparator(pad=(200,1)),
        ],

        [sg.Text('Width', relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text=cvinfos["width"], key="width")
        ],

        [sg.Text('Height', relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text=cvinfos["height"], key="height")
        ],

        [sg.Text('FPS', relief=sg.RELIEF_SUNKEN, size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text=pclx_infos["fps"] or "30", key="fps")
        ],

        [
            sg.Text('Profile',
                    relief=sg.RELIEF_SUNKEN,
                    size=(20, 1),
                    pad=(0, 3)),
            sg.Combo(list(prores_profiles.values()),
                     auto_size_text=True,
                     size=(200,20),
                     key="profile",
                     default_value=prores_profiles[5])
        ],
        [sg.Button('Ok',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   bind_return_key=True,
                   key="doit"),
         sg.VerticalSeparator(),
         sg.Button('Cancel',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   key="-close-")
        ],
        [sg.Text('', relief=sg.RELIEF_SUNKEN,
                 size=(55, 1), pad=(0, 3), key='-status-')]
    ]

def make_movie_event_handler(glbls, subwindows, window_name, target,
                             ffmpeg_profiles, prores_profiles):
    windw, event, values = obtain_subevent(subwindows, window_name)

    if event == "encoding_profile":
        val = values["encoding_profile"]

        if val == None or val == "": return

        prof = ffmpeg_profiles[values["encoding_profile"]]
        for k,v in prof.items(): windw[k].update(v)

    if event == "doit":
        windw['-status-'].Update("Making Movie")

        opts = Options(queue=glbls.queue, window_name=windw.metadata)

        opts.pencil_file = glbls.srcFileName
        opts.height      = values["height"]
        opts.width       = values["width"]
        opts.fps         = values["fps"]
        opts.profile     = {v: k for k, v in
                            prores_profiles.items()}[
                                values["profile"]]

        threading.Thread(target=target, args=(opts, None,), daemon=True).start()
