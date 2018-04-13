# Blenderer

## Description

Blenderer is a Python script that uses multi-processor rendering and FFMPEG library 
to create composite animation videos from blender files. It should work on all 
major operating systems (Windows, MacOS, Linux).

## Instalation

Requirements

- Python 3.4 and above
- Blender 2.70 and above
- FFMPEG 

### Mac OS

```
brew install ffmpeg
```

## Usage

```
renderer somescene.blend -o render.avi
```

All outputs go to directory `output` in the root directory where blender file is located 
