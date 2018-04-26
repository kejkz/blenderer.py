import argparse
import os
import sys

import bpy

SCRIPT_NAME = os.path.basename(__file__)


class WrongColorException(Exception):
    pass


def parse_optional_args():
    argv = sys.argv

    if '--' not in argv:
        argv = []
    else:
        argv = argv[argv.index('--') + 1:]

    usage_text = (
        'Filter or alter the scene in the background:'
        '  blender --background --python {} -- [options]'.format(SCRIPT_NAME)
    )

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument('-t', '--text', type=str, required=True, help='Set the scene text')
    parser.add_argument('-c', '--color', nargs='+', type=float, help='Sets the color of the output (HSV)')
    parser.add_argument('-w', '--watermark', action='store_true', help='Disable watermark rendering')

    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    if not args.text:
        LOGGER.error('--text="some string" argument not given, aborting.')
        parser.print_help()
        return

    return args


def prepare_scene(scene_name, options):
    color = tuple(options.color)
    if len(color) > 3:
        raise WrongColorException('Wrong color for the element')
    bpy.data.objects['Text'].data.body = options.text
    bpy.data.scenes[scene_name].sequence_editor.sequences_all['Color'].color = color
    bpy.data.scenes[scene_name].sequence_editor.sequences_all['watermark.png'].mute = options.watermark


def main(options):
    prepare_scene('Scene', options)


if __name__ == '__main__':
    options = parse_optional_args()
    main(options)
