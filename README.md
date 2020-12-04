PclxTool
---

Python based tool for manipulating ``.pclx`` files generated by
[Pencil2D](https://pencil2d.org).

Provided are features that aren't supported by Pencil2D:

- layer duplication
- scaling of frames (entire layers)
- rotation of frames (entire layers)
- copying of frames
- reversing of frames
- interpolation of object movement between two frames
- layer duplication

Used and tested on MacOS, your mileage will vary on Windows.

Workflow / Integration with Pencil2D
---

The workflow that the tool supports is as follows:

1. Open, edit and save animation in P2D
2. Open PclxTool and drag the Pclx file into PclxTool
3. Apply necessary changes.
4. Each change will generate a new ``.pclx`` file.
5. Open the modified ``.pclx`` in P2D and make changes.
6. Rinse and Repeat

How does it work
---

Pclx files are basically Zip files with one XML file describing the
animation and a data directory with a PNG for each frame of each layer.

PclxTool opens the Zip and applies changes to the XML and PNG files (mostly
directly on the PNGs). It will then create a new pclx file with those changes,
the original pclx file is never changed.

PclxTool only works on Bitmap layers, Vector layers are ignored.

Installation
---

Tested with Python 3.7 on MacOS.

```
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
