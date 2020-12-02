import time, subprocess, types, math, sys, re, optparse, os, signal
import base64, threading, uuid, tempfile
import os.path, xml.dom.minidom, queue

import PySimpleGUIQt as sg

from datetime import datetime
from zipfile  import ZipFile

## local imports
import actions

from helpers import bsn, unzip_pclx, write_new_pclx, thread_do_work
from helpers import pclx_loaded, create_popup, obtain_checked_layers
from helpers import open_with_pencil, obtain_subevent, throw_off_to_thread

from extensions  import Options
from gui.layouts import *
from globals     import FFMPEG_PRORES_PROFILES, FFMPEG_PROFILES, EMACS_CLIENT

sg.theme('SystemDefault')

WhiteRed   = ("white","red")
BlackWhite = ("black","white")

##
## Command line handler
##
def run_as_cli(action, opts):
    glbls = optparse.Values()
    glbls.srcFileName = os.path.abspath(opts.pencil_file)

    tempDir, domtree, obj_elem = unzip_pclx(glbls, glbls.srcFileName)

    ### TODO extend opts with the progress method, else all these
    ### TODO actions will fail.

    os.chdir(tempDir.name)

    if action == 'copy':       actions.multicopy_frames(opts, obj_elem)
    if action == 'delete':     actions.delete_frames(opts, obj_elem)
    if action == 'duplicate':  actions.duplicate_frames(opts, obj_elem)
    if action == 'flop':       actions.mirror_images(opts, obj_elem)
    if action == 'info':       actions.obtain_info(opts, obj_elem, toStdout=True)
    if action == 'merge':      actions.merge_frames(opts, obj_elem)
    if action == 'move':       actions.move_frames_by(opts, obj_elem)
    if action == 'movie':      actions.make_movie(opts, obj_elem)
    if action == 'reverse':    actions.reverse_frames(opts, obj_elem)
    if action == 'rotate':     actions.rotate_frames(opts, obj_elem)
    if action == 'scale':      actions.scale_images(opts, obj_elem)

    os.chdir(tempDir.name)

    if action != 'info' and action != 'movie':
        write_new_pclx(glbls, domtree)

##
## GUI stuff
##
def run_as_gui():

    event_subwindow_lookup = {
        "duplicate": {
            "name": "Duplicate",
            "func": duplicate_layout,
        },
        "reverseframes": {
            "name": "Reverse Frames",
            "func": reverse_frames_layout,
        },
        "deleteframes": {
            "name": "Delete Frames",
            "func": delete_frames_layout,
        },
        "multicopyframes": {
            "name": "Copy Frames",
            "func": multicopy_frames_layout,
        },
        "moveframes": {
            "name": "Move Frames",
            "func": move_frames_layout,
        },
        "rotate": {
            "name": "Rotate",
            "func": rotate_layout,
        },
        "scale": {
            "name": "Scale",
            "func": scale_layout,
        },
        "movealongpath": {
            "name": "Move along a path",
            "func": move_along_path_layout,
        },
        "duplicatelayers": {
            "name": "Duplicate selected layers",
            "func": duplicate_layers_layout,
        },
        "mirrorframes": {
            "name": "Mirror Frames",
            "func": mirror_frames_layout,
        },
    }

    glbls = optparse.Values()
    glbls.main_window = sg.Window(
        'PCLX Helper',
        grab_anywhere=False,
        font=('Helvetica', 12),
        no_titlebar=False,
        alpha_channel=1,
        keep_on_top=False,
        element_padding=(2,3),
        default_element_size=(100, 23),
        default_button_element_size=(120,30),
    ).Layout(main_window_layout())

    subwindows = { "movie": None, "info": None, "gradient_frames": None }
    for k in event_subwindow_lookup.keys(): subwindows[k] = None

    imgwindows = {}

    glbls.srcFileName = None
    glbls.pclx_infos  = None
    glbls.queue       = queue.Queue()

    while True:
        event, values = glbls.main_window.Read(timeout=100)
        if event in (None, 'Exit'):
            break

        if event in event_subwindow_lookup.keys() and pclx_loaded(glbls):
            dt = event_subwindow_lookup[event]
            create_popup(event, subwindows, dt["name"], dt["func"]())

        if event == "movie" and pclx_loaded(glbls):
            create_popup(event, subwindows, "Make Movie",
                         make_movie_layout(glbls.pclx_infos,
                                           FFMPEG_PROFILES,
                                           FFMPEG_PRORES_PROFILES))

        if event == "gradient_frames" and pclx_loaded(glbls):
            create_popup(event, subwindows, "Gradient Frames",
                         gradient_frames_layout(glbls.pclx_infos))

        if event == "emacs":
            if subwindows["info"] == None:
                glbls.main_window['-status-'].Update("No PCLX file loaded")
                continue

            subprocess.call(
                "cd / && {} -n {}".format(EMACS_CLIENT, glbls.srcFileName),
                shell=True)

        if event == "openinpencil2d":
            if subwindows["info"] == None:
                glbls.main_window['-status-'].Update("No PCLX file loaded")
                continue

            open_with_pencil(glbls.srcFileName)

        if event == "addimages":
            if subwindows["info"] == None:
                glbls.main_window['-status-'].Update("No PCLX file loaded")
                continue

            folder = sg.popup_get_folder(
                ('Source folder for images.\nRecursively search the directory '+
                 'and sub-directories for image files and add these in new '+
                 'layers. Each image gets a unique layer.'),
                size=(200,200), title='Select Image Folder')

            if not folder: continue

            opts = Options(queue=glbls.queue, window_name=None)

            opts.folder = folder.replace("file://","")

            threading.Thread(target=thread_do_work,
                             args=(opts, glbls, actions.add_images_as_layers,),
                             daemon=True).start()

        if event == "update":
            if subwindows["info"] == None:
                glbls.main_window['-status-'].Update("No PCLX file loaded")
                continue

            subwindows["info"].Close()
            subwindows["info"] = None
            glbls.main_window['update'].Update(
                disabled=True,
                button_color=WhiteRed
            )

            glbls.main_window['-status-'].Update("Updating")

            tempDir, domtree, obj_elem = unzip_pclx(glbls,
                                                    glbls.srcFileName,
                                                    mainXmlOnly=True)
            if obj_elem != None:
                glbls.pclx_infos = actions.obtain_info(None, obj_elem)
                subwindows["info"] = create_info_window(glbls, obj_elem)

                glbls.main_window['-status-'].Update("Done Update")

            if tempDir != None: tempDir.cleanup()

            glbls.main_window['update'].Update(disabled=False,
                                               button_color=BlackWhite)

        if event == 'FILENAME':
            if values['FILENAME'] == "" or values['FILENAME'] == None:
                glbls.srcFileName = None
                glbls.pclx_infos  = None

                for key in subwindows.keys():
                    if subwindows[key] != None:
                        subwindows[key].Close()
                        subwindows[key] = None

                continue

            if subwindows["info"] != None:
                glbls.main_window['-status-'].Update("Already Loaded")
                continue

            glbls.main_window['-status-'].Update("Loading....")

            def fubar(glbls, subwindows, values):
                tempDir, domtree, obj_elem = unzip_pclx(glbls,
                                                        values['FILENAME'],
                                                        mainXmlOnly=True)

                msg = "No XML Found"
                if obj_elem != None:
                    glbls.pclx_infos = actions.obtain_info(None, obj_elem)
                    subwindows["info"] = create_info_window(glbls, obj_elem)
                    msg = "Done Loading"

                glbls.main_window['-status-'].Update(msg)
                if tempDir != None: tempDir.cleanup()

            threading.Thread(target=fubar,args=(glbls,subwindows,values,),
                             daemon=True).start()

        ##
        ## Queue handling --> these are status updates from the tool windows
        ##
        try:
            dtpt = glbls.queue.get_nowait()

            if "msg" in dtpt.keys():
                try:
                    subwindows[dtpt["window"]]['-status-'].Update(dtpt["msg"])
                except KeyError:
                    glbls.main_window['-status-'].Update(dtpt["msg"])

            if "action" in dtpt.keys():
                if dtpt["action"] == "new_pclx_file":
                    if glbls.main_window['open_new_pclx_in_p2d'].get():
                        open_with_pencil(dtpt["filename"])

                    if glbls.main_window['load_new_pclx_file'].get():
                        subwindows['info'].Close()
                        subwindows['info'] = None
                        glbls.main_window['FILENAME'].Update(
                            dtpt["filename"])

                if dtpt["action"] == "disable_buttons":
                    for k in ["-close-","doit"]:
                        subwindows[dtpt["window"]][k].Update(
                            disabled=True, button_color=WhiteRed)

                if dtpt["action"] == "failure" and dtpt["exception"] != None:
                    imgwindows["_error"] = sg.Window(
                        "Error Happened", layout=error_layout(dtpt["exception"]))

                if (dtpt["action"] == "enable_buttons" or
                    dtpt["action"] == "failure"):
                    for k in ["-close-","doit"]:
                        subwindows[dtpt["window"]][k].Update(
                            disabled=False, button_color=BlackWhite)

                if dtpt["action"] == "show_image_window":
                    srcfile, tlx, tly = dtpt["src"], dtpt["tlx"], dtpt["tly"]

                    if not srcfile in imgwindows.keys():
                        try:
                            data = ZipFile(glbls.srcFileName,'r').read(
                                "data/{}".format(srcfile)
                            )
                            imgwindows[srcfile] = sg.Window(
                                srcfile,
                                layout=show_frame_layout(data,tlx,tly)
                            )
                        except KeyError:
                            imgwindows[srcfile] = sg.Window(
                                srcfile, layout=no_image_data()
                            )

                if dtpt["action"] == "close_image_window":
                    srcfile = dtpt["src"]
                    if srcfile in imgwindows.keys():
                        imgwindows.pop(srcfile).Close()

        except queue.Empty:
            pass

        ##
        ## Check the Image windows (if any)
        ##
        for name in [k for k in imgwindows.keys()]:
            event,values = imgwindows[name].Read(timeout=100)
            if event in (None, 'Exit', '-close-'):
                imgwindows.pop(name).Close()

        ##
        ## Info window event handling
        ##
        if subwindows["info"] != None:
            windw = subwindows["info"]

            if event != 'unload': event, values = windw.Read(timeout=100)

            if event is None or event == 'Exit' or event == 'unload':
                glbls.main_window['-status-'].Update("Unloaded")
                glbls.main_window['FILENAME'].Update("")

            ## toggle the frame buttons to on/off using button_color
            if event != None and event[0:6] == "frame-":
                _,lyid,frnr = event.split("-")

                dtls = glbls.pclx_infos["layers"][lyid]["frame_details"][
                    int(frnr)]

                action = "show_image_window"
                if windw[event].ButtonColor != WhiteRed:
                    windw[event].update( button_color = WhiteRed)
                else:
                    windw[event].update( button_color = BlackWhite)
                    action = "close_image_window"

                glbls.queue.put_nowait({ **dtls, "action": action })
        ##
        ## Handle events from the tool windows.
        ##
        if subwindows["gradient_frames"] != None:
            windw, event, values = obtain_subevent(subwindows, "gradient_frames")

            if event == "doit":
                windw['-status-'].Update("Gradient Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.from_frame  = int(values["from_frame"])
                opts.count       = int(values["count"])
                opts.height      = int(values["height"])
                opts.width       = int(values["width"])
                opts.start_color = values["start_color"]
                opts.end_color   = values["end_color"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.gradient_frames)

        if subwindows["mirrorframes"] != None:
            windw, event, values = obtain_subevent(subwindows, "mirrorframes")

            if event == "doit":
                windw['-status-'].Update("Mirror Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.from_frame      = int(values["from_frame"])
                opts.to_frame        = int(values["to_frame"])
                opts.vertical_flip   = values["vertical_flip"]
                opts.horizontal_flip = values["horizontal_flip"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.mirror_frames)

        if subwindows["movie"] != None:
            windw, event, values = obtain_subevent(subwindows, "movie")

            if event == "encoding_profile":
                val = values["encoding_profile"]

                if val == None or val == "":
                    continue

                prof = FFMPEG_PROFILES[values["encoding_profile"]]
                for k,v in prof.items(): windw[k].update(v)

            if event == "doit":
                windw['-status-'].Update("Making Movie")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.pencil_file = glbls.srcFileName
                opts.height      = values["height"]
                opts.width       = values["width"]
                opts.fps         = values["fps"]
                opts.profile     = {v: k for k, v in
                                    FFMPEG_PRORES_PROFILES.items()}[
                                        values["profile"]]

                threading.Thread(target=actions.make_movie,
                                 args=(opts, None,),
                                 daemon=True).start()

        if subwindows["reverseframes"] != None:
            windw, event, values = obtain_subevent(subwindows, "reverseframes")

            if event == "reverse_all_frames":
                windw["to_frame"].Update(disabled=values["reverse_all_frames"])
                windw["from_frame"].Update(disabled=values["reverse_all_frames"])

            if event == "doit":
                windw['-status-'].Update("Reversing Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.to_frame = None
                if values["to_frame"] != "":
                    opts.to_frame = int(values["to_frame"])

                opts.from_frame = None
                if values["from_frame"] != "":
                    opts.from_frame = int(values["from_frame"])

                opts.all_frames = values["reverse_all_frames"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.reverse_frames)

        if subwindows["deleteframes"] != None:
            windw, event, values = obtain_subevent(subwindows, "deleteframes")

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

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.delete_frames)

        if subwindows["rotate"] != None:
            windw, event, values = obtain_subevent(subwindows, "rotate")

            if event == "extent_x":
                windw["extent_y"].Update(values["extent_x"])

            if event == "duplicate":
                windw["to_frame"].Update(disabled=values["duplicate"])
                windw["count"].Update(disabled=(not values["duplicate"]))

            if event == "rotate_constant":
                windw["rotate_start"].Update(disabled=values["rotate_constant"])

            if event == "extend_frames":
                windw["extent_x"].Update(disabled=(not values["extend_frames"]))
                windw["extent_y"].Update(disabled=(not values["extend_frames"]))

            if event == "doit":
                windw['-status-'].Update("Rotating and Duplicating Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.from_frame      = int(values["from_frame"])
                opts.to_frame        = int(values["to_frame"])
                opts.rotate_step     = float(values["rotate_step"])
                opts.rotate_start    = float(values["rotate_start"])
                opts.count           = int(values["count"])
                opts.extent_x        = int(values["extent_x"])
                opts.extent_y        = int(values["extent_y"])
                opts.extend_frames   = values["extend_frames"]
                opts.rotate_constant = values["rotate_constant"]
                opts.duplicate       = values["duplicate"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.rotate_frames)

        if subwindows["multicopyframes"] != None:
            windw, event, values = obtain_subevent(subwindows, "multicopyframes")

            if event == "doit":
                windw['-status-'].Update("Copying Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.to_frame   = int(values["to_frame"])
                opts.from_frame = int(values["from_frame"])
                opts.count      = int(values["count"])

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.multicopy_frames)

        if subwindows["moveframes"] != None:
            windw, event, values = obtain_subevent(subwindows, "moveframes")

            if event == "move_all_frames":
                windw["to_frame"].Update(disabled=(values["move_all_frames"]))
                windw["from_frame"].Update(disabled=(values["move_all_frames"]))

            if event == "doit":
                windw['-status-'].Update("Moving Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.x_delta = int(values["x_delta"])
                opts.y_delta = int(values["y_delta"])

                opts.to_frame, opts.from_frame = None, None
                if not values["move_all_frames"]:
                    opts.to_frame   = int(values["to_frame"])
                    opts.from_frame = int(values["from_frame"])

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.move_frames_by)

        if subwindows["duplicate"] != None:
            windw, event, values = obtain_subevent(subwindows, "duplicate")

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

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.duplicate_frames)

        if subwindows["scale"] != None:
            windw, event, values = obtain_subevent(subwindows, "scale")

            if event == "duplicate":
                windw["to_frame"].Update(disabled=values["duplicate"])
                windw["count"].Update(disabled=(not values["duplicate"]))

            if event == "scale_constant":
                windw["scale_start"].Update(disabled=values["scale_constant"])

            if event == "doit":
                windw['-status-'].Update("Scaling Frames")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.to_frame       = int(values["to_frame"])
                opts.from_frame     = int(values["from_frame"])
                opts.count          = int(values["count"])
                opts.duplicate      = values["duplicate"]
                opts.scale_step     = float(values["scale_step"])
                opts.scale_start    = float(values["scale_start"])
                opts.scale_constant = values["scale_constant"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.scale_images)

        if subwindows["duplicatelayers"] != None:
            windw, event, values = obtain_subevent(subwindows, "duplicatelayers")

            if event == "doit":
                windw['-status-'].Update("Duplicating Layers")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.count  = int(values["count"])

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.duplicate_layers)

        if subwindows["movealongpath"] != None:
            windw, event, values = obtain_subevent(subwindows, "movealongpath")

            if event == "FILENAME":
                if os.path.isfile(values["FILENAME"].replace("file://","")):
                    windw["to_frame"].Update(disabled=True)
                    windw["count"].Update(disabled=False)

            if event == "browse":
                windw["browse"].Update(disabled=True)
                filename = sg.PopupGetFile("Find SVG",
                                           file_types=(("SVGs","*.svg"),))
                if filename: windw['FILENAME'].Update(filename)
                windw["browse"].Update(disabled=False)

            if event == "doit":
                windw['-status-'].Update("Moving objects along path")

                opts = Options(queue=glbls.queue, window_name=windw.metadata)

                opts.from_frame   = int(values["from_frame"])
                opts.to_frame     = int(values["to_frame"])
                opts.count        = int(values["count"])
                opts.svg_filename = values["FILENAME"]

                throw_off_to_thread(glbls, subwindows["info"], windw,
                                    opts, actions.move_along_path)

    glbls.main_window.Close()

##
## Option parsing
##
if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option(
        '-d', '--debug',
        help="enable debug mode",
        action="store_true", default=False)

    parser.add_option(
        '', '--delete-frames',
        help="when deleting, delete frames not just remove objects in frames",
        action="store_true", default=False)

    parser.add_option(
        '-c', '--count',
        help="duplicate: how many frames to be generated",
        type='int', default=1)
    parser.add_option(
        '-f', '--from-frame',
        help="start which frame",
        type='int', default=None)
    parser.add_option(
        '-t', '--to-frame',
        help="to which frame",
        type='int', default=None)
    parser.add_option(
        '', '--only-x',
        help="when duplicating frames, only update x value",
        action='store_true', default=False)
    parser.add_option(
        '', '--only-y',
        help="when duplicating frames, only update y value",
        action='store_true', default=False)
    parser.add_option(
        '', '--keep-position',
        help="when duplicating frames, don't update the x & y coordinates",
        action='store_true', default=False)

    parser.add_option(
        '-x', '--x-delta',
        help="when moving, this is the delta by which x is moved",
        type='int', default=None)
    parser.add_option(
        '-y', '--y-delta',
        help="when moving, this is the delta by which y is moved",
        type='int', default=None)

    parser.add_option(
        '', '--merge-pencil-file',
        help="merge source file, pclx to take frames from",
        type='str', default=None)
    parser.add_option(
        '', '--merge-from-frame',
        help="the frame in the merge file from where we begin",
        type='int', default=None)
    parser.add_option(
        '', '--merge-to-frame',
        help="the frame in the merge file from where we end",
        type='int', default=None)

    parser.add_option(
        '', '--layers',
        help="comma separate list of layers to work on",
        type='str', default=None)

    parser.add_option(
        '', '--width',
        help="when setting the view size, use this or encoding the movie",
        type='int', default=None)
    parser.add_option(
        '', '--height',
        help="when setting the view size, use this or encoding the movie",
        type='int', default=None)

    parser.add_option(
        '', '--scale-step',
        help="when resizing images, this is the step size",
        type='float', default=None)

    parser.add_option(
        '', '--center-x',
        help="when rotating images, this is the point around which to rotat",
        type='int', default=None)
    parser.add_option(
        '', '--center-y',
        help="when rotating images, this is the point around which to rotat",
        type='int', default=None)
    parser.add_option(
        '', '--rotate-step',
        help="when rotating images, this is the step size",
        type='float', default=None)

    parser.add_option(
        '-p', '--pencil-file',
        help="work on which file",
        type='str', default=None)

    parser.add_option(
        '', '--fps',
        help="Framerate for encoding the movie",
        type='int', default=None)

    parser.add_option(
        '', '--use-gui',
        help="Run in gui mode",
        action='store_true', default=False)

    opts, args = parser.parse_args()

    action = (len(args) > 0 and args[0]) or 'duplicate'

    if opts.use_gui:
        run_as_gui()
    else:
        if opts.pencil_file == None:
            parser.error("Missing args 'to' or 'from' or 'pencil_file'")
            exit(1)

        run_as_cli(action, opts)
