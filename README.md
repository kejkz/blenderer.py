# Blenderer

## Description

Blenderer is a Python script that uses multi-processor
rendering and FFMPEG library to create composite
animation videos from blender files. It should work on
all major operating systems (Windows, MacOS, Linux).

## Instalation

Requirements

- Git (2.6 and above)
- Blender 2.70 and above
  - Python 3.5 (version provided with Blender)
- FFMPEG

### Mac OS

 - Download [blender](https://www.blender.org/download/Blender2.79/blender-2.79b-macOS-10.6.dmg/) and move it to the `/Applications` directory

 - Add blender executable to your path `/Applications/blender/Contents/MacOs/blender`

 - Install `ffmpeg` and add it to your path

```bash
brew install ffmpeg
```

 - Clone the blenderer repository anywhere on system

```bash
git clone git@bitbucket.org:vkaran/blenderer.git
```

- For easier invoking through command line, set environment variable BLENDERER to exact location of `blederer.py` script
```
EXPORT BLENDERER=/path/to/blenderer.py
```

### Windows

WIP

### Linux

Use package manager to install ffmpeg and put it inside
environment path

```
apt-get install blender ffmpeg-lib
```

## Usage

```
blender -b someblenderfile.blend -P $BLENDERER -- -t '"Just Testing"' -c 0.5 0.5 0.5
```

All outputs go to the same directory where blender scene is
located at