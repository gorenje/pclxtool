import subprocess, os.path, tempfile, xml.dom.minidom, re, threading, math, io

from zipfile import ZipFile

BlackWhite = ("black","white")
WhiteRed   = ("white","red")

# basename of file without extension
def bsn(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def to_png(img):
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

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

def obtain_subevent(subwindows, window_name):
    windw = subwindows[window_name]
    event, values = windw.Read(timeout=100)

    if event in (None, 'Exit', '-close-'):
        windw.Close()
        subwindows[windw.metadata] = None

    return (windw, event, values)
