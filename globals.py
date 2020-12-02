LAYER_TYPE_BITMAP = "1"
LAYER_TYPE_CAMERA = "5"

MAX_TO_FRAME_COUNT = 10000

PENCIL2D_APP = "/Applications/Pencil2D.app/Contents/MacOS/pencil2d"
CONVERT_EXE  = "/usr/local/bin/convert"
FFMPEG_EXE   = "/usr/local/bin/ffmpeg"
EMACS_CLIENT = "/Applications/Emacs.app/Contents/MacOS/bin/emacsclient"

ALL_FRAMES = range(1,MAX_TO_FRAME_COUNT)

FFMPEG_PRORES_PROFILES = {
    0: '0 - proxy (sometimes called PR)',
    1: '1 - LT (light)',
    2: '2 - standard (rarely called ST)',
    3: '3 - HQ (high quality)',
    4: '4 - 4444',
    5: '5 - 4444 XQ'
}

FFMPEG_PROFILES = {
    ### 3x HD
    "3xHD 24fps - 4444 XQ": {
        "width": "5760",
        "height": "3240",
        "fps": "24",
        "profile": 5,
    },
    "3xHD 12fps - 4444 XQ": {
        "width": "5760",
        "height": "3240",
        "fps": "12",
        "profile": 5,
    },
    "3xHD 8fps - 4444": {
        "width": "5760",
        "height": "3240",
        "fps": "8",
        "profile": 4,
    },

    ### 2x HD
    "2xHD 24fps - 4444 XQ": {
        "width": "3840",
        "height": "2160",
        "fps": "24",
        "profile": 5,
    },
    "2xHD 12fps - 4444 XQ": {
        "width": "3840",
        "height": "2160",
        "fps": "12",
        "profile": 5,
    },
    "2xHD 8fps - 4444": {
        "width": "3840",
        "height": "2160",
        "fps": "8",
        "profile": 4,
    },

    ### 1x HD
    "1xHD 24fps - 4444 XQ": {
        "width": "1920",
        "height": "1080",
        "fps": "24",
        "profile": 5,
    },
    "1xHD 12fps - 4444 XQ": {
        "width": "1920",
        "height": "1080",
        "fps": "12",
        "profile": 5,
    },
    "1xHD 8fps - 4444": {
        "width": "1920",
        "height": "1080",
        "fps": "8",
        "profile": 4,
    },

}
