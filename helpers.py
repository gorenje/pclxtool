import subprocess, os.path, tempfile, xml.dom.minidom, re, threading, math

from datetime import datetime

import PySimpleGUIQt as sg

from zipfile import ZipFile

## used in the rotate action to maintain rotate factor state
class RotateComputer:
    def __init__(self, opts):
        self._rotate_constant = opts.rotate_constant
        self._rotate_step     = opts.rotate_step
        self._rotate_start    = opts.rotate_start
        self._rotate_by       = opts.rotate_step

    def factor(self):
        if self._rotate_constant: return self._rotate_step

        t = self._rotate_by
        self._rotate_by += self._rotate_step
        return self._rotate_start + t

## used in the scale action to maintain scale factor state
class ScaleComputer:
    def __init__(self, opts):
        self._scale_constant = opts.scale_constant
        self._scale_step     = opts.scale_step
        self._scale_start    = opts.scale_start
        self._scale_by       = opts.scale_step

    def factor(self):
        if self._scale_constant: return self._scale_step

        t = self._scale_by
        self._scale_by += self._scale_step
        return self._scale_start - t


# new src name
def nsn(elem, frame_nr, layer_id=None):
    lyr_id, current_frame_nr, fmt = elem.attributes["src"].value.split(".")
    return "{}.{}.{}".format( "%03d" % int(layer_id or lyr_id),
                              "%03d" % frame_nr, fmt)

# source 'src' attribute value
def src(elem):
    return elem.attributes['src'].value

# top left X value
def tlx(elem):
    return int(elem.attributes['topLeftX'].value)

# top left Y value
def tly(elem):
    return int(elem.attributes['topLeftY'].value)

# top left Y value
def frnr(elem):
    return int(elem.attributes['frame'].value)

# id value
def idvl(elem):
    return int(elem.attributes['id'].value)

# basename of file without extension
def bsn(filename):
    return os.path.splitext(os.path.basename(filename))[0]

# return all images within a layer
def layers(obj_elem):
    return obj_elem.getElementsByTagName('layer')

# return all image tags in the layer element.
def imgs(layer):
    return layer.getElementsByTagName('image')

# find the layer whose name matches the argument
def layer_with_name(layers,name):
    for ly in layers:
        if ly.attributes["name"].value == name:
            return ly
    return None

# compute the frame range from the opts
def compute_frame_range(opts, defrng=range(-2,-1)):
    if opts.to_frame != None and opts.from_frame != None:
        return range(opts.from_frame, opts.to_frame + 1)
    elif opts.to_frame != None:
        return range(1, opts.to_frame)
    elif opts.from_frame != None:
        return range(opts.from_frame, MAX_TO_FRAME_COUNT)

    return defrng

# copy frame
def cpf(elem, frame_nr, layer_id=None):
    subprocess.call("cp -f data/{} data/{}".format(
        src(elem), nsn(elem, frame_nr, layer_id=layer_id)
    ), shell=True)
    return nsn(elem, frame_nr, layer_id=layer_id)

# create temp directory and unzip the pclx into it.
def unzip_pclx(glbls, raw_filename, mainXmlOnly=False):
    tempDir = tempfile.TemporaryDirectory()

    glbls.srcFileName = raw_filename.replace("file://","")

    basename,extension = os.path.splitext(glbls.srcFileName)
    if extension != ".pclx":
        return (None,None,None)

    domtree = None

    if mainXmlOnly:
        tempDir.cleanup()
        mainxml = ZipFile(glbls.srcFileName,"r").read("main.xml")
        domtree = xml.dom.minidom.parseString(mainxml)
        tempDir = None
    else:
        cmdline = "unzip {} -d {} >/dev/null"
        subprocess.call( cmdline.format(glbls.srcFileName, tempDir.name),
                         shell=True)
        domtree  = xml.dom.minidom.parse("{}/main.xml".format(tempDir.name))

    obj_elem = domtree.documentElement.getElementsByTagName('object')[0]

    return (tempDir, domtree, obj_elem)

def write_new_pclx(glbls,domtree):
    with open("main.xml", "w") as f:
        f.seek(0)
        f.write(domtree.toxml())
        f.truncate()

    new_pclx_filename = None
    for seq_num in range(1,10000):
        new_pclx_filename = "{}/{}.{}.pclx".format(
            os.path.dirname(glbls.srcFileName),
            re.sub(r"[.]\d{4}$", "", bsn(glbls.srcFileName)),
            "%04d" % seq_num
        )
        if not os.path.isfile(new_pclx_filename): break

    if new_pclx_filename == None:
            new_pclx_filename = "{}/{}.{}.pclx".format(
                os.path.dirname(glbls.srcFileName),
                re.sub(r"[.]\d{4}$", "", bsn(glbls.srcFileName)),
                datetime.now().strftime("%Y%m%d%H%M%S")
            )

    subprocess.call(
        "zip -r {} main.xml data >/dev/null".format(new_pclx_filename),
        shell=True
    )

    return new_pclx_filename

def create_popup(key, subwindows, title, layout):
    if subwindows[key] != None:
        subwindows[key].bring_to_front()
    else:
        subwindows[key] = sg.Window(title, metadata=key, layout=layout)

def pclx_loaded(glbls):
    if glbls.srcFileName == None:
        glbls.main_window['-status-'].Update("No pclx loaded")
        return False

    return True

def obtain_checked_layers(pclx_info, info_window, this_window):
    layer_ids = []

    if info_window != None:
        for key in info_window.AllKeysDict.keys():
            if key[0:5] == "layer" and info_window[key].get():
                layer_ids.append( key[6:] )

    if len(layer_ids) == 0:
        this_window['-status-'].Update("No Layers Checked")
        return None

    return ",".join([pclx_info["layers"][key]["name"] for key in layer_ids])


def open_with_pencil(filename):
    subprocess.call("open -a Pencil2d {}".format(filename),shell=True)

def obtain_subevent(subwindows, window_name):
    windw = subwindows[window_name]
    event, values = windw.Read(timeout=100)

    if event in (None, 'Exit', '-close-'):
        windw.Close()
        subwindows[windw.metadata] = None

    return (windw, event, values)

def thread_do_work(opts,glbls,target=None):
    if target == None: return

    opts.start_doing()
    tempDir, domtree, obj_elem = unzip_pclx(glbls, glbls.srcFileName)
    os.chdir(tempDir.name)

    try:
        target(opts, obj_elem)
    except Exception as e:
        os.chdir("/")
        if tempDir != None: tempDir.cleanup()
        opts.failed_doing("Something when wrong", e)
        return

    opts.done_doing()

    new_pclx_filename = write_new_pclx(glbls,domtree)
    opts.new_pclx_file(new_pclx_filename)

    os.chdir("/")
    if tempDir != None: tempDir.cleanup()

def throw_off_to_thread(glbls, info_window, windw, opts, target):
    opts.layers = obtain_checked_layers(glbls.pclx_infos, info_window, windw)

    if opts.layers == None: return

    threading.Thread(
        target=thread_do_work,
        args=(opts, glbls, target),
        daemon=True
    ).start()

def apply_rotation(rcc, opts, src_img, convert_exe):
    rotate_by = rcc.factor() # this increments the factor, so only call once

    operator = "-distort SRT '{}'".format(rotate_by)
    if opts.extend_frames:
        operator = (
            "-background none -gravity center -extent {}x{} -distort SRT '{}'"
        ).format(
            opts.extent_x, opts.extent_y, rotate_by,
        )

    subprocess.call(
        "{} data/{} -alpha set {} data/{} >/dev/null 2>&1".format(
            convert_exe, src_img, operator, src_img
        ), shell=True)


def to_points(paths, point_count):
    leng = sum([pt.length() for pt in paths])
    leng_per_point = leng / point_count
    pntcounts, points, total_points = {}, [], 0

    for pth in paths:
        pntcnt = int(math.floor(float(pth.length())/leng_per_point))
        pntcounts[pth] = pntcnt
        total_points += pntcnt

    while total_points < point_count:
        for pth in paths:
            pntcounts[pth] += 1
            total_points += 1

    for pth in paths: points += pth.get_points( pntcounts[pth] )
    return points

def svg_find_tracks(domtree):
    # find paths with the label 'track'
    tracks = [elem for elem in domtree.getElementsByTagName("path")
              if (elem.hasAttribute("inkscape:label") and
                  elem.attributes["inkscape:label"].value == "track")]

    if len(tracks) == 0:
        tracks = []
        # find layers with the label 'track'
        for layer in [ly for ly in domtree.getElementsByTagName("g")
                      if (ly.hasAttribute("inkscape:label") and
                          ly.attributes["inkscape:label"].value == "track")]:

            for path in layer.getElementsByTagName("path"):
                tracks.append(path)

    return tracks
