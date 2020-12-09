import io, PIL

import PySimpleGUIQt as sg

from gui import helpers
from PIL import Image

from .helpers import BlackWhite

def ButtonsAndStatus():
    return [
        [sg.Button('Ok',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   bind_return_key=True,
                   key="doit"),
         sg.VerticalSeparator(),
         sg.Button('Cancel',button_color=BlackWhite,
                   pad=(10,7), border_width=2, size=(7,1),
                   key="-close-")
        ],
        [
            sg.Text('', relief=sg.RELIEF_SUNKEN,
                    size=(55, 1), pad=(0, 3), key='-status-')
        ]
    ]

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

    height = min([1000, (len(infos["layers"].keys()) * 200) + 70])
    return sg.Window(glbls.srcFileName,
                     layout=[[sg.Column(frames, scrollable=True,
                                        size=(1000,height))]],
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
                 sg.B('Move',
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
                 sg.B('Interframe Copy',
                      button_color=BlackWhite,
                      pad=(2,2), size=(13,1),
                      key='multicopyframes'),
             ]]),
         sg.Column([
             [
                 sg.B('Copy with Move',
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
                        size=(25,1),
                        key="open_new_pclx_in_p2d",
                        default=True),
            sg.Checkbox('Immediate Load new Pclx?',
                        size=(25,1),
                        key="load_new_pclx_file",
                        default=True),
            sg.Checkbox('Immediate open movie files?',
                        key="open_new_movie_files",
                        default=True)
        ],
        [
            sg.Column([
                [
                    sg.Text('Drop Pclx File Here'),],[
                    sg.InputText('', size=(300,100),
                                 key='FILENAME', enable_events=True),
                ],
                [sg.B('Update',
                      tooltip="Update the current Pclx",
                      button_color=BlackWhite,
                      size=(10,1),
                      key='update'),
                 sg.VerticalSeparator(pad=(4,4)),
                 sg.B('Browse',
                      tooltip="Browse for new Pclx File",
                      button_color=BlackWhite,
                      size=(10,1),
                      key='browse'),
                 sg.VerticalSeparator(pad=(4,4)),
                 sg.B('Load Empty Pclx',
                      tooltip="Load empty Pclx file",
                      button_color=BlackWhite,
                      size=(10,1),
                      key='load_empty'),
                ],
            ]),
            sg.Column([
                [sg.B('Create Image Layers',
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
                [sg.B('Compact Layers',
                     tooltip="Remove empty frames from layers",
                     button_color=BlackWhite,
                     pad=(2,2), size=(13,1), key='compactlayers')
                ],
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

def no_image_data_layout():
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
            # Use an inputtext here since text can be copied, with sg.Text
            # the contents can't be selected & copied.
            sg.InputText('Size: {}x{} Loc: {}x{}'.format(size_x,size_y,tlx,tly),
                         size=(20, 1), pad=(0, 3))
        ],
        [
            sg.Image(data=helpers.to_png(img))
        ]
    ]

def error_layout(exception):
    return [
        [
            sg.Multiline(exception)
        ]
    ]
