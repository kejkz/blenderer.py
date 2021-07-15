# Blenderer.py

![Blenderer.py](https://github.com/pypvideo/blenderer.py/workflows/Python%20application/badge.svg?branch=master)

## Description

`Blenderer.py` is a Python 3.5 based script that utilizes multi-processor
capabilities and `ffmpeg` library to create composite videos from blender
files. It is designed to work on all major operating systems (Windows, MacOS, Linux).

## Installation

### Requirements

- `git` (2.6 and above)
- `Blender` 2.70 and above
  - `Python` 3.5 (embedded version provided with Blender)
- `ffmpeg` (merging videos)

### Windows 10, 8, 7 (x64)

 - Download [blender](https://www.blender.org/download/Blender2.79/blender-2.79b-windows64.msi/) for Windows

 - Download statically compiled [ffmpeg](https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20180427-4833050-win64-static.zip) and unzip it in any directory on hard drive

 - Clone this repository to a local system

 - Add `ffmpeg` and `blender` executables to Windows `PATH`. Start CMD prompt as an **Administrator** by pressing Windows start button, entering `cmd`, right clicking on the program icon and selecting `Run As Administrator` from the drop-down menu. Then run these two commands:  


```batch
SETX /M PATH "C:\Program Files\ffmpeg\bin;%PATH%"
SETX /M PATH "C:\Program Files\Blender Foundation\Blender\;%PATH%"
SETX /M BLENDERER "C:\Documents\blenderer\blenderer.py"
```

### macOS

 - Download [blender](https://www.blender.org/download/Blender2.79/blender-2.79b-macOS-10.6.dmg/) and move it to the `/Applications` directory

 - Add blender executable to your path `/Applications/blender/Contents/MacOS/blender`

 - Install `ffmpeg` and add it to your path

```bash
brew install ffmpeg
```

 - Clone the `blenderer.py` repository anywhere on system

```bash
git clone git@bitbucket.org:vkaran/blenderer.git
```

- For easier invoking through command line, set environment variable BLENDERER to exact location of `blederer.py` script and add blender executable to the PATH environment variable

```bash
EXPORT PATH=/Applications/blender/Contents/MacOS:$PATH
EXPORT BLENDERER=/path/to/blenderer.py
```

### Linux

- Use package manager to install `ffmpeg` and put it inside
environment path

```
sudo apt-get install blender ffmpeg-lib
```

- Clone repository anywhere on hard drive
- Export `blenderer.py` to the environment either directly ar by adding it to `.bash_profile`

```bash
export BLENDERER=/path/to/blenderer.py
```

## Usage

If everything is added to the environment, you can run
multi-processor rendering using the additional filtering
by calling the blender with these arguments:

```bash
scene_options=$(cat <<EOF
{
  "scene": "Scene",
  "assets": [
    {
      "name": "plc01",
      "hide": true,
      "value": "//Images/image.png"
    },
    {
      "name": "txt01",
      "hide": true,
      "value": "Test Render Layout"
    },
    {
      "name": "txtother01",
      "hide": false,
      "value": "Test Render Layout"
    },
    {
      "name": "ColorScene",
      "hide": false,
      "value": null
    },
    {
      "name": "clr01",
      "hide": true,
      "value": "#001000"
    }
  ]
}
EOF
)
blender -b someblenderfile.blend -P $BLENDERER -- --scene_options "$scene_options"
```

To call a scene rendering without additional filtering:

```bash
blender -b somescene.blend -P $BLENDERER
```

On Windows it's quite similar:

```
blender -b preview.blend -P %BLENDERER%
```

### Command line options overview

There are multiple special command line parameters that `blenderer.py` 
accepts:


It is possible to set an output rendering video path 
by providing the file name from the command line:

```bash
blender -b someblenderfile.blend -P $BLENDERER -- --scene_options "$scene_options" --render_output ~/tmp/render/outputfile.mp4
```

Another option option is to define an images root directory. 
If this option is defined, all of the image objects within the scene
will be prefixed with that directory name as their reference.

```bash
blender -b someblenderfile.blend -P $BLENDERER --  --images-root-dir ~/some_dir_with_images_123
```
