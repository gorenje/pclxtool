import subprocess, os.path, tempfile, xml.dom.minidom, re, threading, math

from datetime import datetime

import PySimpleGUIQt as sg

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

def open_with_pencil(filename):
    subprocess.call("open -a Pencil2d {}".format(filename),shell=True)

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
