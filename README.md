PclxTool
---

Python based tool for manipulating ``.pclx`` files generated by
[Pencil2D](https://pencil2d.org) animation tool. PclxTool is a utility that
provides functionality that Pencil2D does not yet have.

PclxTool was created for doing digital cut-out animations and best supports
that type of animation.

Some provided features:

- layer duplication
- scaling of frames (entire layers)
- rotation of frames (entire layers)
- copying of frames
- reversing of frames
- interpolation of object movement between two frames

Used and tested on MacOS, your mileage will vary on Windows.

A ``.pclx`` (Pclx file) is what Pencil2D saves its animation in. Pclx file
and Pencil2D file are therefore synonyms and are used interchangeably in
this readme. Also, Pencil2D might be abbreviated as P2D. You have been warned :)

All terms that have copyright (I dunno, XML or PNG maybe) are owned to 100%
by those people copyrighting those terms, certainly not me.

Workflow / Integration with Pencil2D
---

The workflow that the tool supports is as follows:

1. Open, edit and save animation in P2D
2. Open PclxTool and drag the Pclx file onto PclxTool
3. Apply necessary changes.
4. Each change will generate a new ``.pclx`` file.
5. Open the modified ``.pclx`` in P2D and make changes....
6. Rinse and Repeat

PclxTool can trigger P2D to load new Pclx files, so changes made in PclxTool
are immediately editable in P2D.

How does it work
---

Pclx files are basically Zip files with one XML file describing the
animation, and a data directory with a PNG for each frame of each layer.

PclxTool unzips the Pclx file and applies changes to the XML and PNG
files (mostly directly on the PNGs). It will then create a new pclx file
with those changes.

**NOTE**: The original pclx file is never changed.

PclxTool only works on Bitmap layers, Vector layers are ignored.

Prerequistes
---

PclxTool [assumes](https://github.com/gorenje/pclxtool/blob/9c1543cfe9faea42fb66bd4e6a1f49f5ffc85994/globals.py#L6-L9) that both [ImageMagick](https://imagemagick.org/index.php) and [FFmpeg](https://ffmpeg.org) are installed and can
be found at:

```
CONVERT_EXE  = "/usr/local/bin/convert"
FFMPEG_EXE   = "/usr/local/bin/ffmpeg"
```

Both of these can be installed via [brew](https://brew.sh).

Also Pencil2D is assumed to be installed at:

```
PENCIL2D_APP = "/Applications/Pencil2D.app/Contents/MacOS/pencil2d"
```

Again, this was tested on MacOS only...

Installation
---

Tested with Python 3.7 on MacOS.

```
git clone git@github.com:gorenje/pclxtool
cd pclxtool
pip3 install -r requirements.txt
```

Running
---

```
python3 tool.py --use-gui
```

Commandline
---

```
python3 tool.py --help
```

The commandline was the original form of this tool, however it has basically
been replaced by the GUI. Some things might still work via the CLI, however,
I've not used it for a long time.

On the other hand, I have no intention of removing the possibility of having
a CLI and will certainly come back to the codebase.

Screencast
---

[Screencast](https://youtu.be/3M8wGqZY7XU) is about 15 mins long and
goes through the steps for creating a simple cut-out animation. The
screencast is broken up into sections, each of which demostrate a
particular functionality of PclxTool.

1. [Installation](https://youtu.be/3M8wGqZY7XU)

PclxTool is a Python-based GUI tool. It uses PySimpleGuiQt as GUI engine
and has been tested on MacOS.

2. [Interface](https://youtu.be/3M8wGqZY7XU?t=15)

PclxTool has one main window for loading Pclx files and apply specific
operations to the file loaded. When a Pencil2D file is loaded, a second
window is opened showing all bitmap layers. Vector layers are ignored and
only a single camera view is supported.

Each operation is applied to one or more layers, these layers are selected
in the layer window.

An operation also has specific parameters and these are shown in the operation
window that is opened when an operation is triggered.

3. [Opening Pclx files](https://youtu.be/3M8wGqZY7XU?t=37)

Pencil2D files can either be opened by dragging them onto PclxTool or by
using the browse button in the main window. In the screencast, only the
drag and drop functionality is demostrated.

4. [Importing Images](https://youtu.be/3M8wGqZY7XU?t=58)

This might seem counterintuitive since Pencil2D already has good support
for image importing. The difference is that, unlike P2D, PclxTool generates
new layers for each image imported. P2D imports images into a single layer,
each image being a new frame. I didn't find a good way to move images
between layers (other than copying and pasting).

5. [Moving along an arc](https://youtu.be/3M8wGqZY7XU?t=94)

Having objects move at constant speed along a path is something that is
difficult to animate. PclxTool provides functionality that allows the user
to define an SVG with a bezier path (or multiple bezier paths) along which
an object will be moved.

The user provides the bezier and the number of frames that it should take for
the object to travel the entire path.

6. [Moving along a line](https://youtu.be/3M8wGqZY7XU?t=188)

Similiar to moving along a path however this takes two frames and moves
object in a straight between the those two frames. New frames are generated
that are evenly spaced so that objects move at a smooth speed.

Example: image i1 is located at 0,0 in frame 1, image i2 is located at
position 10,10 in frame 11. There are no frames between the two images.

```
Frame      1              11
Image    ii@0,0        i2@10,10
```

Moving the image i1 along the path between those frames would result in:

```
Frame      1       2       3       4    ....   8       9      10      11
Image    ii@0,0  i1@1,1  i1@2,2  i1@3,3 .... i1@7,7  i1@8,8  i1@9,9  i2@10,10
```

It doesn't matter what image is in frame 11, of importance is its location
in frame 11.

7. [Gradients](https://youtu.be/3M8wGqZY7XU?t=294)

A gradient frame is a flood-filled single-colour image of the same dimensions
as the camera view.

Gradient frames, as shown in the screencast, can be used to create a background
sky that goes from dark, to blue, to dark again. In the case of the screencast,
this was on conjunction with the sun rising and setting again.

8. [Rotation](https://youtu.be/3M8wGqZY7XU?t=456)

P2D also provides rotation however it is hard to make this constant over
several frames. The rotation operator takes a frame range and rotates all
images either by the same amount (constant rotating) or by a rotation factor
that is additive.

Example: a rotation factor of 8 degrees would rotate the first frame by 8 degs,
the second is rotated by 16 deg, the 3rd by 24 and so on.

9. [Scaling](https://youtu.be/3M8wGqZY7XU?t=559)

Similiar to rotation, scaling scales image, frame for frame, either up
or down. This can be useful for things that get successively smaller as
they move off into the distance.

It also important to note that both rotation and scaling use the original
image, not the image in the previous frame. This means that PclxTool does not
rotate or scale image multiple times, instead each rotation and scaling is based
on the original image.

10. [Frame duplication](https://youtu.be/3M8wGqZY7XU?t=686)

To repeat certain movements over and over again, it's useful to have frame
duplication. In the screencast, this is a sway tree that (rather mechanically)
sways in the wind. The idea is to take a small group of frames, create some
form of movement, then duplicate that entire group to repeat that movement.

11. [Copy with Move](https://youtu.be/3M8wGqZY7XU?t=772)

Copy with move is useful for character movement. The basic idea is that
you have a series of images that form the basis for a walk. As the character
moves, the image are further apart. What copy-with-move does is copy frames
maintaining the distance between images in frames.

Example: let us assume we have a movement that consists of three images,
placed along the layer in four frames (we repeat image 1 for a reason):

```
Frame:   1          2          3          4
Image:  i1  d<1,2> i2  d<2,3> i3  d<3,1> i1
```

We'll call the distance between image i1 and image i2, delta<1,2> or d<1,2>.

When we copy-with-move this sequence, we end up with:

```
Frame:   1          2          3          4         5         6         7
Image:  i1  d<1,2> i2  d<2,3> i3  d<3,1> i1 d<1,2> i2 d<2,3> i3 d<3,1> i1
```

This distance measure is accumulative, meaning that the total distance
between the image in frame 3 (i.e. image 3) and the same image in frame 6
is ``d<3,1> + d<1,2> + d<2,3>``. This distance will be constant for all
subsequent apperances of image 3, i.e. the distane between image 3 in frame 6
and image 3 in frame 9 will be the same.

This can be repeated as often as desired, but results in a smooth
walking character.

Also image i1 was copied into frame 4 so that we have a distance value between
it and image i3 in frame 3, else it would not be possible to know where to
place image i1 in frame 4.

12. [Make ProRes Movies](https://youtu.be/3M8wGqZY7XU?t=862)

Unlike the movie made with Pencil2D, ProRes supports transparency, i.e.,
alpha channel. Films can then be layered on top one another in a
something like [Davinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/).
