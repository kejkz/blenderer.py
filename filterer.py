import argparse
import os
import sys
import json

import bpy

SCRIPT_NAME = os.path.basename(__file__)

# Object types
TEXT_TYPE = 'FONT'
PLACEHOLDER_TYPE = 'MESH'

# Sequence types
SCENE_TYPE = 'SCENE'
AUDIO_TYPE = 'SOUND'
COLOR_TYPE = 'COLOR'


class WrongColorException(Exception):
    pass


def set_object_image(blender_object, imagepath):
    '''Chage file path for a texture assigned to particular object'''
    blender_object.active_material.active_texture.image.filepath = imagepath


def parse_optional_args():
    argv = sys.argv

    if '--' not in argv:
        argv = []
    else:
        argv = argv[argv.index('--') + 1:]

    usage_text = (
        'Filter or alter the scene before rendering:'
        '  blender --background --python {} -- [options]'.format(SCRIPT_NAME)
    )

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument('-so' , '--scene-options', type=json.loads, help='Scene rendering options as JSON')

    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    return args


def prepare_rendering(options):
    '''Prepares the scene before rendering begins'''
    scene_name = scene_options['scene']
    bpy.context.screen.scene = bpy.data.scenes[scene_name]

    try:
        for options in scene_options['objects']:
            blender_object = bpy.data.objects[options['name']]
            blender_object.hide_render = options['render']
            if blender_object.type == TEXT_TYPE:
                blender_object.data.body = options['value']
            elif blender_object.type == PLACEHOLDER_TYPE:
                set_object_image(blender_object, options['value'])
            else:
                print('Unknown object type "{}", skipping...'.format(blender_object.type))
    except KeyError as e:
        print('Missing "%s" modification options in %s', e.value, scene_options)
        exit(1)

    for sequence in scene_options['scenes']:
        currend_seq = bpy.data.scenes[scene_name].sequence_editor.sequences_all[sequence['name']]
        current_seq.mute = sequence['render']
        if current_seq.type == COLOR_TYPE:
            current_seq.color = sequence['value']


def main(options):
    prepare_rendering(options)


if __name__ == '__main__':
    modification_options = parse_optional_args()
    main(options=modification_options.scene_options)
