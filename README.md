# Blenderer

## Description

Blenderer is a Python script that uses multi-processor
rendering and `ffmpeg` library to create composite
animation videos from blender files. It should work on
all major operating systems (Windows, MacOS, Linux).

## Instalation

### Requirements

- git (2.6 and above)
- Blender 2.70 and above
  - Python 3.5 (version provided with Blender)
- ffmpeg (merging videos)

### Windows 10, 8, 7 (x64)

 - Download [blender](https://www.blender.org/download/Blender2.79/blender-2.79b-windows64.msi/) for Windows

 - Download statically compiled [ffmpeg](https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20180427-4833050-win64-static.zip) and unzip it in any directory on hard drive

 - Clone [https://vkaran@bitbucket.org/vkaran/blenderer.git](https://vkaran@bitbucket.org/vkaran/blenderer.git) to a local system

 - Add `ffmpeg` and `blender` executables to Windows `PATH`. Start CMD prompt as an **Administrator** by pressing Windows start button, entering `cmd`, right clicking on the program icon and selecting `Run As Administrator` from the drop-down menu. Then run these two commands:

 ```
 SETX /M PATH "C:\Program Files\ffmpeg\bin;%PATH%"
 SETX /M PATH "C:\Program Files\blender;%PATH%"
 SETX /M BLENDERER "C:\Documents\blenderer\blenderer.py"
 ```

### macOS

 - Download [blender](https://www.blender.org/download/Blender2.79/blender-2.79b-macOS-10.6.dmg/) and move it to the `/Applications` directory

 - Add blender executable to your path `/Applications/blender/Contents/MacOS/blender`

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

### Linux

- Use package manager to install ffmpeg and put it inside
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
multi-processor rendering script using something similar
as script provided

```
blender -b someblenderfile.blend -P $BLENDERER -- -t '"Just Testing"' -c 0.5 0.5 0.5
```

Video output file is created in the same path as set in
scene rendering.