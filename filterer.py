import argparse
import os
import sys
import json
import mathutils
import struct
import urllib.request
import urllib.parse

import bpy

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

class SceneFormatException(Exception):
    pass

def download_image_from(url):
    '''Download image and return stored absolute file path'''
    local_path = os.path.join(DOWNLOAD_PATH, os.path.basename(url))
    if not os.path.isdir(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    urllib.request.urlretrieve(url, local_path)
    return os.path.abspath(local_path)


def set_object_image(blender_object, imagepath):
    '''Change file path for a texture assigned to particular object'''
    blender_object.active_material.active_texture.image.filepath = imagepath


def hex_to_rgb(rgb_str):
    int_tuple = struct.unpack('BBB', bytes.fromhex(rgb_str.lstrip('#')))
    return tuple([val/255 for val in int_tuple])


class SceneModifier:
    scene_key = 'scene'
    assets_key = 'assets'

    def __init__(self, filtering_options, images_root_path):
        try:
            self.scene = filtering_options[self.scene_key]
            self.assets = filtering_options[self.assets_key]
        except KeyError as e:
            print('Missing "%s" section in %s', e.value, scene_options)
            raise SceneFormatException(e.value)
        self.images_root_path = images_root_path

    def set_scene(self):
        '''
        Set the scene for the filtering context.
        NOTE: Quite important for rendering if scene was not set to active
        '''
        bpy.context.screen.scene = bpy.data.scenes[self.scene]

    def find_object(self, objname):
        '''
        Find object by trying accessing both objects list and scene
        '''
        try:
            blender_object = bpy.data.objects[objname]
        except KeyError:
            blender_object = bpy.data.scenes[self.scene].sequence_editor.sequences_all[objname]
        return blender_object

    def hide_object(self, blender_object):
        try:
            blender_object.mute
            print('object hidden succesfully {}'.format(blender_object))
        except AttributeError:
            blender_object.hide_render = True
            print('object hidden succesfully after attribute error: {}'.format(blender_object))

    def modify_object(self, blender_object, options):
        if options['hide']:
            self.hide_object(blender_object)

        if blender_object.type == TEXT_TYPE:
            blender_object.data.body = options['value']
        elif blender_object.type == PLACEHOLDER_TYPE:
            if options['value']:
                url = urllib.parse.urlparse(options['value'])
                if 'http' in url.scheme:
                    local_path = download_image_from(url.geturl())
                else:
                    local_path = url.path
                set_object_image(blender_object, local_path)
        elif blender_object.type == COLOR_TYPE:
            blender_object.color = hex_to_rgb(options['value'])
        else:
            print('Unknown object type "{}", skipping object {}'.format(
                blender_object.type, options['name']))

    def modify_images_root_path(self):
        if self.images_root_path:
            for image in bpy.data.images.values():
                image.filepath = os.path.join(
                    self.images_root_path,
                    bpy.path.basename(image.filepath)
                )
                print('Altered filepath: {}'.format(image.filepath))

    def alter_scene(self):
        self.modify_images_root_path()
        for options in self.assets:
            blender_object = self.find_object(options['name'])
            self.modify_object(blender_object, options)
