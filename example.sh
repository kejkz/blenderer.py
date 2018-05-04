#!/bin/sh

scene_options=$(cat <<EOF
{
  "scene": "Scene",
  "objects": [
    {
      "name": "plc01",
      "render": true,
      "value": "//Images/image.png"
    },
    {
      "name": "txt01",
      "render": true,
      "value": "Test Render Layout"
    },
    {
      "name": "txtother01",
      "render": false,
      "value": "Test Render Layout"
    }
  ],
  "sequences": [
    {
      "name": "ColorScene",
      "render": false,
      "value": null
    },
    {
      "name": "clr01",
      "render": true,
      "value": "#001000"
    }
  ]
}
EOF
)

blender -b $1 -P $BLENDERER -- --scene-options "$scene_options"
