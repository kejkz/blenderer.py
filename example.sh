#!/bin/sh

blender -b $1 -P $BLENDERER -- -t "Just Testing" -c 0.5 0.5 0.5
