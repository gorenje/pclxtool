import time, subprocess, types, math, sys, re, optparse, os, signal
import base64, threading, uuid, tempfile
import os.path, xml.dom.minidom, queue

import PySimpleGUIQt as sg

from datetime import datetime
from zipfile  import ZipFile

## local imports
import actions

from helpers import pclx_loaded, create_popup, open_with_pencil

from gui import *

from gui.extensions import Options
from gui.layouts    import *
from gui.helpers    import write_new_pclx, thread_do_work, unzip_pclx

from globals import FFMPEG_PRORES_PROFILES, FFMPEG_PROFILES, EMACS_CLIENT

sg.theme('SystemDefault')

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
            "lyot": duplicate_frames_layout,
            "hdlr": duplicate_frames_event_handler,
            "actn": actions.duplicate_frames,
        },
        "reverseframes": {
            "name": "Reverse Frames",
            "lyot": reverse_frames_layout,
            "hdlr": reverse_frames_event_handler,
            "actn": actions.reverse_frames,
        },
        "deleteframes": {
            "name": "Delete Frames",
            "lyot": delete_frames_layout,
            "hdlr": delete_frames_event_handler,
            "actn": actions.delete_frames,
        },
        "multicopyframes": {
            "name": "Copy Frames",
            "lyot": multicopy_frames_layout,
            "hdlr": multicopy_frames_event_handler,
            "actn": actions.multicopy_frames,
        },
        "moveframes": {
            "name": "Move Frames",
            "lyot": move_frames_layout,
            "hdlr": move_frames_event_handler,
            "actn": actions.move_frames_by,
        },
        "compactlayers": {
            "name": "Compact Layers",
            "lyot": compact_layers_layout,
            "hdlr": compact_layers_event_handler,
            "actn": actions.compact_layers,
        },
        "rotate": {
            "name": "Rotate",
            "lyot": rotate_layout,
            "hdlr": rotate_frames_event_handler,
            "actn": actions.rotate_frames,
        },
        "scale": {
            "name": "Scale",
            "lyot": scale_frames_layout,
            "hdlr": scale_frames_event_handler,
            "actn": actions.scale_images,
        },
        "duplicatelayers": {
            "name": "Duplicate selected layers",
            "lyot": duplicate_layers_layout,
            "hdlr": duplicate_layers_event_handler,
            "actn": actions.duplicate_layers,
        },
        "mirrorframes": {
            "name": "Mirror Frames",
            "lyot": mirror_frames_layout,
            "hdlr": mirror_frames_event_handler,
            "actn": actions.mirror_frames,
        },
        "movealongpath": {
            "name": "Move along a path",
            "lyot": move_along_path_layout,
            "hdlr": move_along_path_event_handler,
            "actn": actions.move_along_path,
        },
        "gradient_frames": {
            "hdlr": gradient_background_event_handler,
            "actn": actions.gradient_frames,
        }
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

    subwindows = { "movie": None, "info": None }
    for k in event_subwindow_lookup.keys(): subwindows[k] = None

    imgwindows = {}

    glbls.srcFileName = None
    glbls.pclx_infos  = None
    glbls.queue       = queue.Queue()

    events_with_layouts = [k for k in event_subwindow_lookup.keys()
                           if ("name" in event_subwindow_lookup[k].keys() and
                               "lyot" in event_subwindow_lookup[k].keys())]

    events_with_handlers = [k for k in event_subwindow_lookup.keys()
                            if ("hdlr" in event_subwindow_lookup[k].keys() and
                                "actn" in event_subwindow_lookup[k].keys())]

    while True:
        event, values = glbls.main_window.Read(timeout=100)

        # event == "__TIMEOUT__"

        if event in (None, 'Exit'):
            break

        if event in events_with_layouts and pclx_loaded(glbls):
            dt = event_subwindow_lookup[event]
            create_popup(event, subwindows, dt["name"], dt["lyot"]())

        if event == "movie" and pclx_loaded(glbls):
            create_popup(event, subwindows, "Make Movie",
                         make_movie_layout(glbls.pclx_infos,
                                           FFMPEG_PROFILES,
                                           FFMPEG_PRORES_PROFILES))

        if event == "gradient_frames" and pclx_loaded(glbls):
            create_popup(event, subwindows, "Gradient Frames",
                         gradient_background_layout(glbls.pclx_infos))

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

            folder = sg.PopupGetFolder(
                ('Source folder for images. Directory (and subdirectories) \n'+
                 'will be recursively searched for image files (png, jpg, \n'+
                 'gif) and added as a new layer. One layer, one image.'),
                default_path=(
                    os.path.dirname(os.path.abspath(__file__)) +
                    "/assets/example/elements"),
                title='Select Image Folder')

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

        if event == "browse":
            glbls.main_window["browse"].Update(disabled=True,
                                               button_color=WhiteRed)

            filename = sg.PopupGetFile("Find Pencil2D File",
                                       file_types=(("P2D","*.pclx"),))
            if filename:
                glbls.main_window['FILENAME'].Update(filename)

            glbls.main_window["browse"].Update(disabled=False,
                                               button_color=BlackWhite)

        if event == "load_empty":
            glbls.main_window['FILENAME'].Update(
                os.path.dirname(os.path.abspath(__file__)) + "/assets/empty.pclx"
            )

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
                subwindows["info"].Close()
                subwindows["info"] = None

            glbls.main_window['-status-'].Update("Loading....")

            def load_pclx(glbls, subwindows, values):
                tempDir, domtree, obj_elem = unzip_pclx(glbls,
                                                        values['FILENAME'],
                                                        mainXmlOnly=True)

                msg = "No XML Found"
                if obj_elem != None:
                    glbls.pclx_infos = actions.obtain_info(None, obj_elem)
                    subwindows["info"] = create_info_window(glbls, obj_elem)
                    msg = "Done Loading"

                glbls.main_window['-status-'].Update(msg)

            threading.Thread(target=load_pclx,
                             args=(glbls,subwindows,values,),
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
                if dtpt["action"] == "new_movie_file":
                    if glbls.main_window['open_new_movie_files'].get():
                        subprocess.call("open '{}'".format(dtpt["filename"]),
                                        shell=True)

                if dtpt["action"] == "new_pclx_file":
                    if glbls.main_window['open_new_pclx_in_p2d'].get():
                        open_with_pencil(dtpt["filename"])

                    if glbls.main_window['load_new_pclx_file'].get():
                        subwindows['info'].Close()
                        subwindows['info'] = None
                        glbls.main_window['FILENAME'].Update(
                            dtpt["filename"])

                if (dtpt["action"] == "disable_buttons" and
                    dtpt["window"] != None):
                    for k in ["-close-","doit"]:
                        subwindows[dtpt["window"]][k].Update(
                            disabled=True, button_color=WhiteRed)

                if dtpt["action"] == "failure" and dtpt["exception"] != None:
                    imgwindows["_error"] = sg.Window(
                        "Error Happened", layout=error_layout(dtpt["exception"]))

                if (dtpt["action"] == "enable_buttons" or
                    dtpt["action"] == "failure") and dtpt["window"] != None:
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
                                srcfile, layout=no_image_data_layout()
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
        for subwinname in events_with_handlers:
            if subwindows[subwinname] != None:
                dtls = event_subwindow_lookup[subwinname]
                dtls["hdlr"](glbls, subwindows, subwinname, dtls["actn"])

        if subwindows["movie"] != None:
            make_movie_event_handler(glbls,
                                     subwindows,
                                     "movie",
                                     actions.make_movie,
                                     FFMPEG_PROFILES,
                                     FFMPEG_PRORES_PROFILES)

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
