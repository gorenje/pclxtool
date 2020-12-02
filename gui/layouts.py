import io, PIL

import PySimpleGUIQt as sg

from gui import icons, helpers
from PIL import Image

BlackWhite = ("black","white")

def create_info_window(glbls, obj_elem):
    frames = []
    infos  = glbls.pclx_infos

    for cvid in infos["cv"].keys():
        info = infos["cv"][cvid]

        frames.append(
            [
                sg.Text(info["name"],
                        relief=sg.RELIEF_SUNKEN,
                        text_color="Black",
                        size=(20, 1), pad=(0, 3)),
                sg.Text("{}x{}".format(info["width"], info["height"]),
                        relief=sg.RELIEF_SUNKEN,
                        text_color="Black",
                        size=(20, 1), pad=(0, 3)),
            ]
        )

    frames.append(
        [
            sg.Text("Layer Count",
                    relief=sg.RELIEF_SUNKEN,
                    text_color="Black",
                    size=(20, 1), pad=(0, 3)),
            sg.Text("{}".format(len(infos["layers"].keys())),
                    relief=sg.RELIEF_SUNKEN,
                    text_color="Black",
                    size=(20, 1), pad=(0, 3)),
        ]
    )

    for lyid in infos["layers"].keys():
        info = infos["layers"][lyid]

        buttons = [
            sg.Checkbox(info["name"], default=False,
                        size=(25, 1),
                        key="layer-{}".format(lyid)),

            sg.Column([
                [
                    sg.Text("Diff X",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3)),
                    sg.Text(info["diff_x"],
                            tooltip="X Diff",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3))
                ],

                [
                    sg.Text("Diff Y",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3)),
                    sg.Text(info["diff_y"],
                            tooltip="Y Diff",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3))
                    ],

                [
                    sg.Text("Frames",
                            tooltip="X Diff",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3)),
                    sg.Text(info["frame_count"],
                            tooltip="Frame Count",
                            relief=sg.RELIEF_SUNKEN,
                            text_color="Black",
                            size=(5, 1), pad=(0, 3))
                ],
            ]),
        ]

        frame_buttons, prev_frame_nr = [], 0
        for framenr in info["frame_numbers"]:

            if (prev_frame_nr+1) != framenr:
                frame_buttons.append(sg.VerticalSeparator())

            prev_frame_nr = framenr

            frame_buttons.append(
                sg.Button(str(framenr),
                          button_color=BlackWhite,
                          pad=(5,2),
                          border_width=2,
                          size=(3,1),
                          key="frame-{}-{}".format(lyid, framenr))
            )

        buttons.append(sg.Column([frame_buttons],
                                 scrollable=True,
                                 size=(400,80)) )

        bgclr = "#cccccc" if info["visible"] else "#999999"
        frames.append([
            sg.Frame('', [buttons], title_color='white',
                     background_color=bgclr,
                     pad=(10,10))
        ])

    return sg.Window(glbls.srcFileName,
                     layout=[[sg.Column(frames, scrollable=True,
                                        size=(1000,1500))]],
                     grab_anywhere=False,
                     font=('Helvetica', 12),
                     no_titlebar=False,
                     alpha_channel=1,
                     keep_on_top=False,
                     element_padding=(2,3),
                     default_element_size=(100, 23),
                     default_button_element_size=(120,30))

## To avoid issue with layouts being reused, need to generate these
## layouts using a function ...
def toolbar_buttons():
     return [[
             sg.Text("Frame Actions", text_color="Black",
                     justification="center",
                     size=(65,1))
         ],
         [
         sg.Column([
             [
                 sg.B('Rotate',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='rotate')
             ],[
                 sg.B('Scale',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='scale'),
             ],[
                 sg.B('Gradient Frames',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='gradient_frames'),
             ]]),
         sg.Column([
             [
                 sg.B('Constant Move',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='moveframes'),
             ],[
                 sg.B('Reverse',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='reverseframes'),
             ],[
                 sg.B('Mirror Frames',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='mirrorframes'),
             ]]),
         sg.Column([
             [
                 sg.B('Delete',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='deleteframes'),
             ],[
                 sg.B('Multi-Copy',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='multicopyframes'),
             ]]),
         sg.Column([
             [
                 sg.B('Duplicate with Move',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='duplicate'),
             ],[
                 sg.B('Move along Path',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='movealongpath'),
             ]])
     ]]

def main_window_layout():
    return [
        [sg.Frame('', toolbar_buttons(), title_color='white',
                  background_color=sg.COLOR_SYSTEM_DEFAULT, pad=(10,10))
        ],
        [
            sg.Checkbox('Open new Pclx in Pencil2d?',
                        size=(30,1),
                        key="open_new_pclx_in_p2d",
                        default=True),
            sg.Checkbox('Immediate Load new Pclx?',
                        key="load_new_pclx_file",
                        default=True)
        ],
        [
            sg.Column([
                [
                    sg.InputText('Drop Pclx File Here', size=(300,100),
                                 key='FILENAME', enable_events=True),
                ],
                [sg.B('Update',
                     tooltip="Update the current Pclx",
                     button_color=BlackWhite,
                     pad=(0,0), size=(10,1), key='update'),
                 sg.VerticalSeparator(pad=(10,10)),
                 sg.B('Unload',
                     tooltip="Unload the current Pclx",
                     button_color=BlackWhite,
                     pad=(0,0), size=(10,1), key='unload')
                ],
            ]),
            sg.Column([
                [sg.B('Add Images',
                     tooltip="Add images to Pclx - one per layer",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='addimages')
                ],
                [sg.B('Duplicate Layers',
                     tooltip="Duplicated checked layers",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='duplicatelayers')
                ],
                [sg.B('Open In Pencil2D',
                     tooltip="Open current Pclx in p2d",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='openinpencil2d')
                ],
                [sg.B('Open In Emacs',
                     tooltip="Open current Pclx in emacs",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='emacs')
                ]
            ]),
            sg.Column([
                [sg.B('Make Movie',
                     tooltip="Make Apple ProRes Movie",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='movie')
                ],
            ]),
        ],
        [sg.Text('Welcome to PclxTool',
                 relief=sg.RELIEF_SUNKEN,
                 size=(65, 1),
                 pad=(0, 3),
                 key='-status-')]
    ]

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

def scale_layout():
    return [
        [sg.Text('Scale an image by percent. Scale step is additive and\n'+
                 'is increment which each frame. If duplicate is checked,\n'+
                 'then to frame is ignoreed and count number of from-frames\n'+
                 'are created and then scaled. If scaling by constant is \n'+
                 'selected, then that scaling factor will be used for all \n'+
                 'frames.')
        ],
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

        [sg.Checkbox('Duplicate Frames', key="duplicate",
                     default=False,
                     enable_events=True)],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10",
                      key="count",
                      disabled=True)],

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

def reverse_frames_layout():
    return [
        [
            sg.Checkbox('Reverse All Frames', key="reverse_all_frames",
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

def move_frames_layout():
    return [
        [
            sg.Button('', image_data=icons.coords64)
        ],
        [
            sg.Text('X Delta', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="x_delta"),
            sg.Text('Y Delta', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="0", key="y_delta")
        ],

        [
            sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="1", key="from_frame"),

            sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                    size=(10, 1), pad=(0, 3)),
            sg.InputText(default_text="10", key="to_frame"),
            sg.Checkbox('All Frames', key="move_all_frames",
                        default=False, enable_events=True)
        ],

        [
            sg.Button('Ok',button_color=BlackWhite,
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


def delete_frames_layout():
    return [
        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],
        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")],
        [sg.Checkbox('Delete Frames', key="delete_frames")],
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

def no_image_data():
    return [
        [sg.Text(
            'No Image Data, Frame Blank.'
        )],
    ]

def show_frame_layout(image_data, tlx, tly):
    img = PIL.Image.open(io.BytesIO(image_data))
    size_x, size_y = img.size
    if size_y > 256 or size_x > 256: img.thumbnail((256,256))

    return [
        [
            sg.InputText('Size: {}x{} Loc: {}x{}'.format(size_x,size_y,tlx,tly),
                         size=(20, 1), pad=(0, 3))
        ],
        [
            sg.Image(data=helpers.to_png(img))
        ]
    ]

def rotate_layout():
    return [
        [sg.Text(
            'Rotate frames by degrees. If you want to rotate an image\n'+
            'about its center, without cropping, then extend its canvas\n'+
            'beforehand.\n'
        )],

        [sg.Text('Start Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="to_frame")
        ],

        [sg.Checkbox('Constant Rotating', key="rotate_constant",
                     default=False,
                     enable_events=True)],

        [sg.Text('Rotate Step', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1.5", key="rotate_step")
        ],

        [sg.Text('Rotate Start', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="0", key="rotate_start")
        ],

        [sg.Checkbox('Extend canvas before rotation',
                     key="extend_frames", default=False, enable_events=True)
        ],
        [
            sg.Text('Extend To', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="0",
                         key="extent_x",
                         enable_events=True,
                         disabled=True),
            sg.Text(',', size=(2, 1), pad=(0, 1)),
            sg.InputText(default_text="0", key="extent_y",disabled=True)
        ],

        [
            sg.Checkbox('Duplicate Frames', key="duplicate",
                        default=False,
                        enable_events=True)
        ],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="count", disabled=True)
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
                 size=(40, 1), pad=(0, 3), key='-status-')]
    ]

def gradient_frames_layout(pclx_infos):
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

        [
            sg.Radio('Vertical Flip', group_id="a",
                     key="vertical_flip", default=True),
        ],[
            sg.Radio('Horizonal Flip', group_id="a",
                     key="horizontal_flip"),
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

def duplicate_layout():
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

def multicopy_frames_layout():
    return [
        [sg.Text("Start Frame",
                 relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="1", key="from_frame")],

        [sg.Text('End Frame', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="10", key="to_frame")],

        [sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                 size=(20, 1), pad=(0, 3)),
         sg.InputText(default_text="2", key="count")],

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

def duplicate_layers_layout():
    return [
        [
            sg.Text('Count', relief=sg.RELIEF_SUNKEN,
                    size=(20, 1), pad=(0, 3)),
            sg.InputText(default_text="2", key="count")
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

def error_layout(exception):
    return [
        [
            sg.Multiline(exception)
        ]
    ]
