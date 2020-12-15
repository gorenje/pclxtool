import subprocess, os, os.path, tempfile, re, glob

from datetime import datetime

from globals import *
from helpers import *
from svg     import svg_path
from PIL     import Image as pilImg

import geometry as fg
import colour   as clr

# move frames in layers by x-delta and y-delta. Can be limited by
# frame numbers
def move_frames_by(opts, obj_elem):
    move_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    x_delta  = (opts.x_delta or 0)
    y_delta  = (opts.y_delta or 0)
    frnr_rng = compute_frame_range(opts, defrng=ALL_FRAMES)

    for layer in obj_elem.getElementsByTagName('layer'):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in move_layers):

            for elem in imgs(layer):
                if frnr(elem) in frnr_rng:
                    if opts.abscoords:
                        if (not opts.y_only):
                            elem.attributes['topLeftX'] = str(opts.x_abscoords)
                        if (not opts.x_only):
                            elem.attributes['topLeftY'] = str(opts.y_abscoords)
                    else:
                        if (not opts.y_only):
                            elem.attributes['topLeftX'] = str(
                                tlx(elem) + x_delta)
                        if (not opts.x_only):
                            elem.attributes['topLeftY'] = str(
                                tly(elem) + y_delta)


# flop is horizontal flip - flop all images in the pclx (except vec)
def mirror_frames(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    frm_rng = compute_frame_range(opts)

    prgstr = ""
    for layer in obj_elem.getElementsByTagName('layer'):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format(layer.attributes["name"].value,prgstr)
            opts.progress(prgstr)

            if opts.all_frames:
                frnrs   = [frnr(elem) for elem in imgs(layer)]
                frm_rng = range(min(frnrs), max(frnrs) + 1)

            for elem in imgs(layer):
                if frnr(elem) in frm_rng:
                    oper = "-flop"
                    if opts.horizontal_flip: oper = "-flip"

                    subprocess.call("{} {} data/{} data/{}".format(
                        CONVERT_EXE, oper, src(elem), src(elem)), shell=True)

# reverse the order of the layers by renumbering them.
def reverse_frames(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    for layer in obj_elem.getElementsByTagName('layer'):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            opts.progress(layer.attributes["name"].value)

            if opts.all_frames:
                max_frame_nr = max([frnr(e) for e in imgs(layer)])

                for elem in imgs(layer):
                    elem.attributes['frame'] = str(max_frame_nr -
                                                   frnr(elem) + 1)
            else:
                frm_rng = compute_frame_range(opts)
                frm_nr_lookup = dict(zip(frm_rng, reversed(frm_rng)))
                for elem in imgs(layer):
                    if frnr(elem) in frm_rng:
                        elem.attributes['frame'] = str(frm_nr_lookup[frnr(elem)])

# remove frames including their images.
def delete_frames(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    delete_frames = opts.delete_frames or False
    rng = compute_frame_range(opts)

    prgstr = ""
    for layer in obj_elem.getElementsByTagName('layer'):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format(layer.attributes["name"].value,prgstr)
            opts.progress(prgstr)

            if opts.all_frames:
                rng = range(1, max([frnr(e) for e in imgs(layer)]) + 1)

            for elem in imgs(layer):
                if frnr(elem) in rng:
                    if delete_frames:
                        subprocess.call("rm -f data/{}".format(src(elem)),
                                        shell=True)
                        layer.removeChild(elem)
                    else:
                        subprocess.call(
                            "{} -size 0x0 xc:transparent data/{}".format(
                                CONVERT_EXE, src(elem)), shell=True)

# take a source and destination frame and move an object along a path
# between the two frames.
# The frames in-between will be created as needed.
#
#   Frame 1 - From           Frame 10 - To
#     Obj at 1,1       ....   Obj at 10,10
#
# This will create frame 2 where object is at 2,2, frame 3 where object
# is at 3,3, Frame 4 ... etc until frame 9 where the object is at 9,9
def move_along_path(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    if (opts.to_frame == None or opts.from_frame == None or
        opts.to_frame == "" or opts.from_frame == ""):
        opts.failed_doing("Source and/or Destination frames not provided")
        return

    # Was an SVG file provided with a path that we should follow?
    path_to_follow = None
    if (opts.svg_filename and
        os.path.isfile(opts.svg_filename.replace("file://",""))):

        domtree = xml.dom.minidom.parse(opts.svg_filename.replace("file://",""))
        tracks = svg_find_tracks(domtree)

        if len(tracks) == 0:
            return opts.failed_doing("SVG: Couldn't find track, "+
                                     "rename a layer to 'track'")

        svg_tag = domtree.getElementsByTagName("svg")[0]

        # everything needs to be scaled since the coordinate system is relative
        # to the viewBox and not to the width + height of the document.
        viewbox = (svg_tag.getAttribute("viewbox") or
                   svg_tag.getAttribute("viewBox")).split(" ")

        if viewbox[0] != '0' or viewbox[1] != '0':
            return opts.failed_doing("SVG: Unknown ViewBox type: {}".format(
                viewbox))

        width = float(svg_tag.getAttribute("width"))
        height = float(svg_tag.getAttribute("height"))

        scale_factor = ( ( width / float(viewbox[2]) ) +
                          ( height / float(viewbox[3]) ) ) / 2.0

        # svg coordinate system has top-left as 0,0 however p2d has
        # 0,0 in the middle of the canvas. So all points have to be
        # moved .... by half the size of the document.
        path_to_follow = (
            [ (pt * scale_factor) - fg.Point(width / 2.0, height / 2.0)
              for pt in svg_path( tracks[0].attributes ).getGeometry()]
        )
        opts.to_frame = opts.count + opts.from_frame

    prgstr = ""
    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format(layer.attributes["name"].value,prgstr)
            opts.progress(prgstr)

            src_frame, dest_frame, all_imgs = None, None, {}

            for img in imgs(layer):
                if frnr(img) == opts.from_frame: src_frame  = img
                if frnr(img) == opts.to_frame:   dest_frame = img
                all_imgs[frnr(img)] = img

            points = []
            # get_points from Line also returns the srcpt and destpt,
            # we don't want these points, we want all points in-between.
            # Also the number of points is frame distance plus one b
            # ecauase we remove 2 points - the first and last points.
            if path_to_follow:
                points = to_points(path_to_follow,
                                   opts.to_frame - opts.from_frame + 1)[1:-1]
            else:
                srcpt  = fg.Point( tlx(src_frame),  tly(src_frame) )
                destpt = fg.Point( tlx(dest_frame), tly(dest_frame) )

                points = fg.Line(srcpt, destpt).get_points(
                    frnr(dest_frame) - frnr(src_frame) + 1)[1:-1]

            last_frame = src_frame

            for pt in points:
                new_frame_nr = frnr(last_frame) + 1

                # If an existing frame exists, then move it, don't replace
                # it.
                if new_frame_nr in all_imgs.keys():
                    last_frame = all_imgs[new_frame_nr]
                    last_frame.attributes['topLeftX'] = str(int(pt.x))
                    last_frame.attributes['topLeftY'] = str(int(pt.y))
                else:
                    cln_elem = last_frame.cloneNode(0)

                    cln_elem.attributes['frame'] = str(new_frame_nr)
                    cln_elem.attributes['src'] = cpf(cln_elem, new_frame_nr)

                    cln_elem.attributes['topLeftX'] = str(int(pt.x))
                    cln_elem.attributes['topLeftY'] = str(int(pt.y))

                    last_frame = layer.insertBefore(cln_elem, last_frame)

# merge two pclx's together to make one large pclx
def merge_frames(opts, obj_elem):
    merge_file = os.path.abspath(opts.merge_pencil_file)
    merge_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    merge_rng = range(-2,-1)
    if opts.merge_to_frame != None and opts.merge_from_frame != None:
        merge_rng = range(opts.merge_from_frame, opts.merge_to_frame + 1)

    if opts.merge_to_frame != None:
        merge_rng = range(1, opts.merge_to_frame)
    elif opts.merge_from_frame != None:
        merge_rng = range(opts.merge_from_frame, MAX_TO_FRAME_COUNT)

    tmpdir = tempfile.TemporaryDirectory()
    subprocess.call( "unzip {} -d {} 2>&1 >/dev/null".format(
        merge_file, tmpdir.name), shell=True)

    merge_dom      = xml.dom.minidom.parse("{}/main.xml".format(tmpdir.name))
    merge_obj_elem = merge_dom.documentElement.getElementsByTagName('object')[0]

    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in merge_layers):

            layer_id   = int(layer.attributes["id"].value)
            last_frame = sorted(imgs(layer), key=frnr, reverse=True)[0]
            from_layer = layer_with_name(layers(merge_obj_elem),
                                         layer.attributes["name"].value)
            if from_layer:
                # order by frame number, else we'll merge in reverse
                for img in sorted(imgs(from_layer), key=frnr):
                    if frnr(img) in merge_rng:
                        cln_elem = img.cloneNode(1)
                        new_src = nsn(img, frnr(last_frame)+1, layer_id=layer_id)

                        subprocess.call("cp -f {}/data/{} data/{}".format(
                            tmpdir.name, src(img), new_src
                        ), shell=True)

                        cln_elem.attributes["frame"] = str(frnr(last_frame)+1)
                        cln_elem.attributes["src"] = new_src

                        last_frame = layer.insertBefore(cln_elem, last_frame)

# scale all images by a percent step X.
def scale_images(opts, obj_elem):
    scale_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    prgstr = ""
    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in scale_layers):

            prgstr = "{},{}".format(layer.attributes["name"].value,prgstr)
            opts.progress(prgstr)
            scc = ScaleComputer(opts)

            if opts.duplicate:
                src_frame, last_frame = None, None
                max_frame_nr = max([frnr(e) for e in imgs(layer)])

                for img in imgs(layer):
                    if frnr(img) == opts.from_frame: src_frame  = img
                    if frnr(img) == max_frame_nr:    last_frame = img

                for cnt in range(1, opts.count + 1):
                    new_frame_nr                = max_frame_nr + cnt
                    cln_img                     = src_frame.cloneNode(0)
                    cln_img.attributes['frame'] = str(new_frame_nr)
                    cln_img.attributes['src']   = cpf(cln_img, new_frame_nr)

                    subprocess.call("{} data/{} -scale {}% data/{}".format(
                        CONVERT_EXE, src(cln_img), scc.factor(),
                        src(cln_img)), shell=True)

                    if opts.center_after_scaling:
                        with pilImg.open("data/{}".format(src(cln_img))) as img:
                            cln_img.attributes['topLeftX'] = str(
                                int(img.width / -2.0))
                            cln_img.attributes['topLeftY'] = str(
                                int(img.height / -2.0))

                    last_frame = layer.insertBefore(cln_img, last_frame)

                    opts.progress("{} {}".format(prgstr,cnt))

            else:
                frnr_rng = compute_frame_range(opts, defrng=ALL_FRAMES)
                for img in sorted(imgs(layer), key=frnr):
                    if frnr(img) in frnr_rng:
                        subprocess.call("{} data/{} -scale {}% data/{}".format(
                            CONVERT_EXE, src(img), scc.factor(), src(img)),
                                        shell=True)

                        opts.progress("{} {}".format(prgstr,frnr(img)))

# Rotate frames in layer.
def rotate_frames(opts,obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    prgstr = ""

    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format(prgstr,
                                    layer.attributes["name"].value)
            opts.progress(prgstr)
            rcc = RotateComputer(opts)

            if opts.duplicate:
                max_frame_nr          = max([frnr(e) for e in imgs(layer)])
                last_frame, src_frame = None, None

                for img in imgs(layer):
                    if frnr(img) == opts.from_frame: src_frame  = img
                    if frnr(img) == max_frame_nr:    last_frame = img

                    if src_frame == None or last_frame == None: continue

                for cnt in range(1, opts.count + 1):
                    opts.progress("{} - {}".format(prgstr,cnt))

                    new_frame_nr                = max_frame_nr + cnt
                    cln_img                     = src_frame.cloneNode(0)
                    cln_img.attributes['frame'] = str(new_frame_nr)
                    cln_img.attributes['src']   = cpf(cln_img, new_frame_nr)

                    apply_rotation(rcc, opts, src(cln_img), CONVERT_EXE)

                    last_frame = layer.insertBefore(cln_img, last_frame)
            else:
                frnr_rng = compute_frame_range(opts, defrng=ALL_FRAMES)
                for img in sorted(imgs(layer), key=frnr):
                    if frnr(img) in frnr_rng:
                        opts.progress("{} - {}".format(prgstr,frnr(img)))
                        apply_rotation(rcc, opts, src(img), CONVERT_EXE)

# Encode using Apple ProRes codec with transparency. This can then be used
# in Davinci Resolve.
def make_movie(opts, obj_elem):
    opts.start_doing()

    src_file = os.path.abspath(opts.pencil_file)

    width  = opts.width  or "1920"
    height = opts.height or "1080"
    fps    = opts.fps    or "10"
    tmpdir = tempfile.TemporaryDirectory()

    basename, extname = os.path.splitext(src_file)
    os.chdir(tmpdir.name)

    opts.progress("Starting pencil2d")
    exitcode = subprocess.call(
        ("{} --transparency --width {} --height {} -o image.png {} "+
         ">/dev/null 2>&1").format(PENCIL2D_APP, width, height, src_file),
        shell=True)

    if exitcode != 0:
        opts.failed_doing("P2d Failed - {}".format(exitcode))
        tmpdir.cleanup()
        os.chdir("/")
        return None

    movie_name = None
    for seq_num in range(1,10000):
        movie_name = "{}.{}.mov".format(
            re.sub(r"[.]\d{4}$", "", basename),
            "%04d" % seq_num
        )
        if not os.path.isfile(movie_name): break

    if movie_name == None:
        movie_name = "{}.{}.mov".format(
            re.sub(r"[.]\d{4}$", "", basename),
            datetime.now().strftime("%Y%m%d%H%M%S")
        )

    # https://avpres.net/FFmpeg/im_ProRes.html --> profile value 5 avoids getting
    #    "[prores_ks @ 0x7fb5f7138400] Underestimated required buffer size"
    # errors when encoding large videos
    opts.progress("Starting ffmpeg")
    exitcode = subprocess.call(
        ("{} -y -framerate {} -i image%04d.png -profile:v {} -vcodec prores_ks "+
         "-pix_fmt yuva444p10le {} >/dev/null 2>&1").format(
             FFMPEG_EXE, fps, opts.profile, movie_name), shell=True)

    if exitcode != 0:
        opts.failed_doing("FFmpeg Failed - {}".format(exitcode))
        tmpdir.cleanup()
        os.chdir("/")
        return None

    os.chdir("/")
    opts.done_doing()
    opts.new_movie_file(movie_name)

# Multi-Copy frames --> take a frame range and copy each frame X times, i.e.:
#   copy frames 2 to 4 three times each would like like this:
#
#    1   2     3     4    5  6
#    |  /|\   /|\   /|\   |  |
#    1 2 3 4 5 6 7 8 9 10 11 12
#
# So frame 1 remains 1, frame 2 becomes frames 2,3,4, 3 --> 5,6,7 ... and
# frame 5 becomes 11, 6 --> 12...
#
# --> can be used to make certian movements appear slow where others are
# fast because the framerate is increased.
def multicopy_frames(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    # create a lookupmap.... current_frame_number to new_frame_number
    cur_to_new,new_frame_cntr = {}, 1
    for idx in range(1, opts.from_frame):
        cur_to_new[idx] = [new_frame_cntr]
        new_frame_cntr += 1

    for idx in range(opts.from_frame, opts.to_frame+1):
        cur_to_new[idx] = []
        for cnt in range(opts.count):
            cur_to_new[idx].append(new_frame_cntr)
            new_frame_cntr += 1

    for idx in range(opts.to_frame+1, MAX_TO_FRAME_COUNT):
        cur_to_new[idx] = [new_frame_cntr]
        new_frame_cntr += 1

    # clone the individual images into the right spots.
    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            new_images = []
            for img in imgs(layer):
                for new_frame_nr in cur_to_new[frnr(img)]:
                    cln_img = img.cloneNode(0)
                    cln_img.attributes['src'] = cpf(cln_img, new_frame_nr)
                    cln_img.attributes['frame'] = str(new_frame_nr)
                    new_images.append(cln_img)

            new_layer = layer.cloneNode(0)
            [new_layer.appendChild(img) for img in new_images]
            obj_elem.replaceChild(new_layer, layer)


# duplicate frames, moving images along the X-axis (or y-axis) using the
# relative distances between existing frames, e.g.
#  duplicate the four frames, three times:
#
#    1 2 3 4
#
# becomes
#
#    1 2 3 4 5 6 7 8 9 10 11 12 13
#    1 2 3 4 2 3 4 2 3  4  2  3  4
#
# because we take the distance that objects travelled between frames 1 & 2
# and ensure that the objects are moved that far when they get appened to
# the end of the frames. so the objects in frame 5 have moved the same amount
# that the objects original moved between frames 1 and 2 but they've moved
# in relation to their position in frame 4.
#
# ==> this is good for animating steps where the feet make the same movement
# ==> but move along the frame.
def duplicate_frames(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)]
    )

    orig_to_frame   = opts.to_frame
    orig_from_frame = opts.from_frame

    prgstr = ""
    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format( layer.attributes["name"].value, prgstr)
            opts.progress(prgstr)

            last_frame_nr = max([frnr(e) for e in imgs(layer)])

            if opts.all_frames:
                opts.to_frame   = last_frame_nr
                opts.from_frame = min([frnr(e) for e in imgs(layer)])
            else:
                frnums = [frnr(e) for e in imgs(layer)]
                opts.to_frame   = min([ max(frnums), orig_to_frame ])
                opts.from_frame = max([ min(frnums), orig_from_frame ])

            frame_rng = range(opts.from_frame, opts.to_frame + 1)
            frames_to_copy, ref_frame, last_frame, all_imgs = {}, None, None, {}

            for elem in imgs(layer):
                fnr           = frnr(elem)
                all_imgs[fnr] = elem

                if fnr in frame_rng:       frames_to_copy[fnr] = elem
                if fnr == opts.from_frame: ref_frame  = elem
                if fnr == last_frame_nr:   last_frame = elem

            copy_range = range(1, opts.to_frame - opts.from_frame + 1)

            ## The move existing option implies that we start moving frames
            ## directly after the to/from-frame-range instead of appending
            ## new frames after the very last frame.
            ##
            ##         +---> start here if move_existing is set
            ##         |       +---> start here if move_existing is not set
            ##         V       V
            ##   1 2 3 4 5 6 7 - - - -
            ##   \. ./
            ##     V
            ##     +----> the to/from-frame range
            ##
            ## But don't replace the image --> existing frames are moved,
            ## not replaced.
            if opts.move_existing: last_frame = all_imgs[opts.to_frame]

            ## If where moving the objects in the frame relatively to
            ## their movements in previous frames, then we start at the
            ## second frame (else we don't have diff values). If we're
            ## just duplicating, then we ignore diff values and copy the frames
            ## "as they are" from the previous location, and include the initial
            ## frame.
            if opts.keep_position or opts.duplicate_all:
                new_frame_nr = opts.to_frame + 1

                if opts.duplicate_all:
                    copy_range = range(0, opts.to_frame - opts.from_frame + 1)

                for cnt in range(1, opts.count+1):
                    for idx in copy_range:
                        if new_frame_nr in all_imgs.keys():
                            # existing frames are left unchanged. this only
                            # makes sense if we're are moving frames.
                            pass
                        else:
                            src_elem = frames_to_copy.get(opts.from_frame + idx)
                            if src_elem:
                                cln_elem = src_elem.cloneNode(0)
                                cln_elem.attributes['src'] = cpf(cln_elem,
                                                                 new_frame_nr)
                                cln_elem.attributes['frame'] = str(new_frame_nr)
                                last_frame = layer.insertBefore(cln_elem,
                                                                last_frame)

                        new_frame_nr += 1
            else:
                details_for_frame = {}
                for idx in frame_rng:
                    d = {
                        "fnr":    idx,
                        "diff_x": tlx(frames_to_copy[idx]) - tlx(ref_frame),
                        "diff_y": tly(frames_to_copy[idx]) - tly(ref_frame)
                    }

                    ref_frame = frames_to_copy[idx]
                    details_for_frame[idx-opts.from_frame] = d

                for cnt in range(1, opts.count+1):
                    for idx in copy_range:
                        frm_dtls = details_for_frame[idx]

                        new_frame_nr = frnr(last_frame)+1

                        if new_frame_nr in all_imgs.keys():
                            chg_elem = all_imgs[new_frame_nr]

                            if not opts.only_y:
                                chg_elem.attributes['topLeftX'] = str(
                                    tlx(last_frame) + frm_dtls["diff_x"])

                            if not opts.only_x:
                                chg_elem.attributes['topLeftY'] = str(
                                    tly(last_frame) + frm_dtls["diff_y"])

                            last_frame = chg_elem
                        else:
                            cln_elem = frames_to_copy[frm_dtls['fnr']].cloneNode(0)
                            cln_elem.attributes['src'] = cpf(cln_elem,
                                                             new_frame_nr)
                            cln_elem.attributes['frame'] = str(new_frame_nr)

                            if not opts.only_y:
                                cln_elem.attributes['topLeftX'] = str(
                                    tlx(last_frame) + frm_dtls["diff_x"])

                            if not opts.only_x:
                                cln_elem.attributes['topLeftY'] = str(
                                    tly(last_frame) + frm_dtls["diff_y"])

                            last_frame = layer.insertBefore(cln_elem, last_frame)


# remove all empty frames from a layer and move existing frames up
# correspondingly.
def compact_layers(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            opts.progress(layer.attributes["name"].value)

            current_frame_nr = 1
            for elem in sorted(imgs(layer), key=frnr):
                if frnr(elem) != current_frame_nr:
                    orig_src, old_frm_nr = src(elem), frnr(elem)
                    elem.attributes["frame"] = str(current_frame_nr)
                    elem.attributes["src"] = cpf(elem, current_frame_nr)
                current_frame_nr += 1

# duplicate an entire layer...
def duplicate_layers(opts, obj_elem):
    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    new_id_value = max([idvl(layer) for layer in layers(obj_elem)]) + 1

    for layer in layers(obj_elem):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            opts.progress(layer.attributes["name"].value)

            for cnt in range(1, (opts.count or 1) + 1):
                cln_layer = layer.cloneNode(0)

                new_layer_name = "{} COPY {}".format(
                    layer.attributes["name"].value, cnt
                )
                cln_layer.attributes["id"] = str(new_id_value)
                cln_layer.attributes["name"] = new_layer_name

                for img in imgs(layer):
                    cln_img = img.cloneNode(0)
                    cln_img.attributes["src"] = cpf(img, frnr(img), new_id_value)
                    cln_layer.appendChild(cln_img)

                opts.progress("{} --> {}".format(layer.attributes["name"].value,
                                                 new_layer_name))
                new_id_value += 1
                obj_elem.insertBefore(cln_layer, layer)

# Add images to the pclx, one new layer per image
def add_images_as_layers(opts, obj_elem):
    filenames = [f for f in (
        glob.glob(opts.folder + "/**/*.png", recursive=True) +
        glob.glob(opts.folder + "/**/*.jpeg",recursive=True) +
        glob.glob(opts.folder + "/**/*.jpg", recursive=True) +
        glob.glob(opts.folder + "/**/*.gif", recursive=True)
    )]

    new_id_value = max([idvl(layer) for layer in layers(obj_elem)]) + 1

    base_layer, base_image = None, None
    for layer in layers(obj_elem):
        if layer.attributes["type"].value == LAYER_TYPE_BITMAP:
            base_layer = layer.cloneNode(0)
            base_image = imgs(layer)[0].cloneNode(0)
            break

    for f in filenames:
        opts.progress(f)
        cln_layer = base_layer.cloneNode(0)
        cln_img = base_image.cloneNode(0)

        filename = "{}.001.png".format( "%03d" % new_id_value )
        cln_layer.attributes["id"] = str(new_id_value)
        cln_layer.attributes["name"] = bsn(f)

        # reduce the image to a bear minimum, removing any empty landscape and
        # convert to png.
        with pilImg.open(f) as img:
            img.crop(img.getbbox()).save("data/{}".format(filename))

        cln_img.attributes["src"] = filename
        cln_img.attributes["frame"] = "1"
        cln_img.attributes["topLeftY"] = "0"
        cln_img.attributes["topLeftX"] = "0"

        cln_layer.appendChild(cln_img)
        obj_elem.appendChild(cln_layer)
        new_id_value += 1

def gradient_frames(opts,obj_elem):
    strt_color = clr.Color(opts.start_color)
    end_color  = clr.Color(opts.end_color)
    clr_range  = [c for c in strt_color.range_to(end_color, opts.count)]

    # 0,0 is middle and topleft is -X,-Y, half of the camera view.
    loc = fg.Point( -opts.width, -opts.height ) * (1/2.0)

    apply_to_layers = (opts.layers and opts.layers.split(",")) or (
        [elem.attributes["name"].value for elem in layers(obj_elem)])

    prgstr = ""
    for layer in obj_elem.getElementsByTagName('layer'):
        if (layer.attributes["type"].value == LAYER_TYPE_BITMAP and
            layer.attributes["name"].value in apply_to_layers):

            prgstr = "{},{}".format(layer.attributes["name"].value,prgstr)
            opts.progress(prgstr)

            cln_frame, all_imgs = None, {}
            for img in imgs(layer):
                all_imgs[frnr(img)] = img
                cln_frame = img

            if cln_frame == None: continue

            for fnr in range(opts.from_frame, opts.count+opts.from_frame):
                opts.progress("{} - {}".format(prgstr, fnr))

                elem = None
                if fnr in all_imgs.keys():
                    elem = all_imgs[fnr]

                    elem.attributes['topLeftX'] = str(int(loc.x))
                    elem.attributes['topLeftY'] = str(int(loc.y))

                    cln_frame = elem
                else:
                    elem = cln_frame.cloneNode(0)

                    elem.attributes['frame'] = str(fnr)
                    elem.attributes['src']   = nsn(cln_frame, fnr)
                    elem.attributes['topLeftX'] = str(int(loc.x))
                    elem.attributes['topLeftY'] = str(int(loc.y))

                    cln_frame = layer.insertBefore(elem, cln_frame)

                pilImg.new("RGB", (opts.width,opts.height),
                           clr_range[fnr - opts.from_frame].get_hex()).save(
                               "data/{}".format(src(elem)))


# obtain infos about the image layers
def obtain_info(opts, obj_elem, toStdout=False):
    info = { "cv": {},  "layers": {}, "fps": None }

    info["fps"] = obj_elem.parentNode.getElementsByTagName(
        'projectdata')[0].getElementsByTagName(
            'fps')[0].attributes["value"].value

    for layer in layers(obj_elem):
        if layer.attributes["type"].value == LAYER_TYPE_CAMERA:
            info["cv"][layer.attributes["id"].value] = {
                "name":   layer.attributes["name"].value,
                "width":  layer.attributes["width"].value,
                "height": layer.attributes["height"].value
            }

        if layer.attributes["type"].value == LAYER_TYPE_BITMAP:
            frame_nums = [frnr(e) for e in imgs(layer)]

            if frame_nums == []:
                info["layers"][layer.attributes["id"].value] = {
                    "name":          layer.attributes["name"].value,
                    "diff_x":        0,
                    "diff_y":        0,
                    "visible":       layer.attributes["visibility"].value == "1",
                    "frame_count":   0,
                    "frame_numbers": [],
                    "frame_details": {}
                }
                continue

            max_frame_nr = max(frame_nums)
            min_frame_nr = min(frame_nums)

            first_frame, last_frame, image_count = None, None, 0
            frame_details = {}

            for elem in imgs(layer):
                image_count += 1
                fnr = frnr(elem)
                if fnr == min_frame_nr: first_frame = elem
                if fnr == max_frame_nr: last_frame  = elem
                frame_details[fnr] = {
                    "src": src(elem),
                    "tlx": tlx(elem),
                    "tly": tly(elem)
                }

            info["layers"][layer.attributes["id"].value] = {
                "name":          layer.attributes["name"].value,
                "diff_x":        tlx(first_frame) - tlx(last_frame),
                "diff_y":        tly(first_frame) - tly(last_frame),
                "visible":       layer.attributes["visibility"].value == "1",
                "frame_count":   image_count,
                "frame_numbers": sorted(frame_nums),
                "frame_details": frame_details
            }

    if toStdout:
        for cvids in info["cv"].keys():
            cview = info["cv"][cvids]
            print("Camera View '{}': {}x{}".format(
                cview["name"], cview["width"], cview["height"]))

        for lyid in info["layers"].keys():
            layer = info["layers"][lyid]
            print("Diff for {}: x: {} y: {} Frames: {}".format(
                "%20s" % layer["name"],
                "%3d"  % layer["diff_x"],
                "%3d"  % layer["diff_y"],
                layer["frame_count"]))

    return info
