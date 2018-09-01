#!/bin/sh
blender_path=$(which blender)
blender --version
echo "blender path: ${blender_path}"
echo "blenderer.py path: ${BLENDERER}"

scene_options=$(cat <<EOF
{
  "scene": "Scene",
  "assets": [
    {
      "name": "plc01",
      "hide": true,
      "value": "https://dl.dropboxusercontent.com/s/pn37zg96h7je0ch/coca-cola.png"
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

blender -b $1 -P $BLENDERER -- --scene-options "$scene_options"
