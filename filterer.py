import argparse
import os
import sys
import json
import mathutils
import struct
import urllib3
import urllib.parse

import bpy

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_PATH = os.path.join(os.path.dirname(bpy.data.filepath), 'Images')

# Object types
TEXT_TYPE = 'FONT'
PLACEHOLDER_TYPE = 'MESH'

# Sequence types
SCENE_TYPE = 'SCENE'
AUDIO_TYPE = 'SOUND'
COLOR_TYPE = 'COLOR'


class WrongColorException(Exception):
    pass


def download_image(url):
    '''Download image and return stored absolute file path'''
    local_path = os.path.join(DOWNLOAD_PATH, os.path.basename(url.path))
    http = urllib3.PoolManager()
    r = http.request('GET', url.geturl(), preload_content=False)
    chunk_size = 512

    with open(local_path, 'wb') as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            out.write(data)

    r.release_conn()
    return os.path.abspath(path)


def set_object_image(blender_object, imagepath):
    '''Chage file path for a texture assigned to particular object'''
    blender_object.active_material.active_texture.image.filepath = imagepath


def hex_to_rgb(rgb_str):
    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str.lstrip('#')))
    return tuple([val/255 for val in int_tuple])


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


def prepare_rendering(scene_options):
    '''Prepares the scene before rendering begins'''
    scene_name = scene_options['scene']
    bpy.context.screen.scene = bpy.data.scenes[scene_name]

    try:
        for options in scene_options['objects']:
            blender_object = bpy.data.objects[options['name']]
            blender_object.hide_render = options['hide']
            if blender_object.type == TEXT_TYPE:
                blender_object.data.body = options['value']
            elif blender_object.type == PLACEHOLDER_TYPE:
                if options['value']:
                    url = urllib.parse.urlparse(options['value'])
                    if url.scheme == 'http':
                        local_path = download_image(url)
                    else:
                        local_path = url.path
                    set_object_image(blender_object, local_path)
            else:
                print('Unknown object type "{}", skipping...'.format(blender_object.type))
    except KeyError as e:
        print('Missing "%s" modification options in %s', e.value, scene_options)
        exit(1)

    for sequence in scene_options['sequences']:
        current_seq = bpy.data.scenes[scene_name].sequence_editor.sequences_all[sequence['name']]
        current_seq.mute = sequence['hide']
        if current_seq.type == COLOR_TYPE:
            current_seq.color = hex_to_rgb(sequence['value'])


def main(options):
    prepare_rendering(options)


if __name__ == '__main__':
    modification_options = parse_optional_args()
    main(options=modification_options.scene_options)
