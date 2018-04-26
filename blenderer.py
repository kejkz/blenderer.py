import os
import bpy
import sys
import argparse
import logging
import multiprocessing
import subprocess
import math
import tempfile
from typing import NamedTuple
from collections import namedtuple


RenderingOptions = namedtuple(
    'RenderingOptions',
    [
        'total_frames',
        'frames_per_second',
        'start_frame',
        'end_frame',
        'file_format',
        'video_format',
        'video_codec',
        'x_resolution',
        'y_resolution'
    ]
)

class NotEnoughFramesException(Exception):
    pass


class BlenderVersionMismatchException(Exception):
    pass


class BlenderRenderingError(Exception):
    pass


class ResolutionNotDivisableException(Exception):
    pass


class UpdateAutoSplitException(Exception):
    pass


def check_blender_version():
    blender_file_version = bpy.data.version
    blender_app_version = bpy.app.version
    if not blender_file_version == blender_app_version:
        error_text = 'Blender file %s version and version of the blender app %s do not match'
        LOGGER.warning(error_text, blender_file_version, blender_app_version)
    return blender_app_version


def init_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter()
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger


LOGGER = init_logger(__name__, logging.DEBUG)

RESERVED_CORES = 0
LOGICAL_CORES = multiprocessing.cpu_count()
CORES_ENABLED = LOGICAL_CORES - RESERVED_CORES
AUTO_DELETE_TEMP = True
AUTO_OVERWRITE = True
SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_PATH = os.path.realpath(__file__)
ROOT_PATH = os.path.dirname(bpy.data.filepath)
FILTER_SCRIPT_PATH = os.path.join(SCRIPT_PATH, 'filterer.py')

BLENDER_VERSION = check_blender_version()
BLENDER_EXEC_PATH = bpy.app.binary_path
BLENDER_FILE_PATH = os.path.join(ROOT_PATH, bpy.path.basename(bpy.context.blend_data.filepath))
BLENDER_ENGINE = 'BLENDER_RENDER'
VIDEO_EXTENSION = 'mp4'
OUTPUT_FILE_PATH = '{}.{}'.format(os.path.splitext(bpy.context.blend_data.filepath)[0], VIDEO_EXTENSION)

AUDIO_MIXRATES = ('44100', '48000', '96000', '192000', )
BLENDER_IMAGE_FORMATS = (
    'BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA',
    'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EX', 'HDR', 'TIFF', )

TEMP_DIR = tempfile.TemporaryDirectory(prefix='renderer')

def check_file_exist():
    if not BLENDER_FILE_PATH:
        raise ValueError('Cannot render empty file!')


def set_output_extension(render_options: RenderingOptions) -> str:
    if render_options.file_format in ('AVI_JPEG', 'AVI_RAW'):
        return 'avi'
    elif render_options.video_format in ('AVI', 'H264', 'XVID'):
        return 'avi'
    elif render_options.video_format == 'DV':
        return 'dv'
    elif render_options.video_format == 'FLASH':
        return 'flv'
    elif render_options.video_format == 'MKV':
        return 'mkv'
    elif render_options.video_format == 'MPEG1':
        return 'mpg'
    elif render_options.video_format == 'MPEG2':
        return 'dvd'
    elif render_options.video_format == 'MPEG4':
        return 'mp4'
    elif render_options.video_format == 'OGG':
        return 'ogv'
    elif render_options.video_format == 'QUICKTIME':
        return 'mov'


def render_command(start_frame, end_frame, output_file_path, filter_options=None):
    '''Creates a render command for all of the plaforms'''
    return '{} -b {} -P {} -s {} -e {} -o {} -a -- {}'.format(
        BLENDER_EXEC_PATH, BLENDER_FILE_PATH, FILTER_SCRIPT_PATH,
        start_frame, end_frame, output_file_path, ' '.join(filter_options))


def merge_command(concat_file_path):
    '''Merge temporary video output files'''
    return 'ffmpeg -f concat -safe 0 -y -i {} -c copy {}'.format(concat_file_path, OUTPUT_FILE_PATH)


def audio_command(input_file):
    '''Merges audio from original video to a final video file'''
    return 'ffmpeg -y -i {} -c:v copy -c:a copy -map 0:v:0 -map 1:a:0 -movflags faststart {}'.format(input_file, OUTPUT_FILE_PATH)


def temp_video_file_path(core, start_frame, end_frame):
    output_filename = os.path.join(
        TEMP_DIR.name,
        '{}_{}-{}.{}'.format(core, start_frame, end_frame, VIDEO_EXTENSION))
    return output_filename


def call_render_commands(commands):
    processes = [subprocess.Popen(com, shell=True) for com in commands]
    exit_codes = [p.wait() for p in processes]

    if 1 in exit_codes:
        raise BlenderRenderingError('Something went wrong with rendering process')


def render(start_frame, total_frames, filter_options):
    portion_of_frames_per_core = math.ceil(total_frames / CORES_ENABLED)
    end_frame = start_frame + portion_of_frames_per_core

    concat_video_list_path = os.path.join(TEMP_DIR.name, 'concat_video_list.txt')
    concat_file_paths = []
    render_commands = []

    for core in range(1, CORES_ENABLED + 1):
        output_file_path = temp_video_file_path(core, start_frame, end_frame)
        command = render_command(start_frame, end_frame, output_file_path, filter_options)
        LOGGER.info('Rendering command:\n %s', command)
        render_commands.append(command)
        concat_file_paths.append(output_file_path)
        start_frame = end_frame + 1
        end_frame += portion_of_frames_per_core


    with open(concat_video_list_path, 'w') as f:
        for video in concat_file_paths:
            f.write("file '{}'\n".format(video))

    call_render_commands(render_commands)

    merge_video_files_command = merge_command(concat_video_list_path)

    LOGGER.debug(merge_video_files_command)

    subprocess.call(merge_video_files_command, shell=True)

    TEMP_DIR.cleanup()


def check_cpu():
    if CORES_ENABLED == 1:
        LOGGER.warning('%s script utilizes multiple logical cores, and this system have only 1', SCRIPT_NAME)
        return
    LOGGER.info('Utilizing %i cores', CORES_ENABLED)


def audio_options():
    post_full_audio = '-c:v copy -c:a copy -map 0:v:0 -map 1:a:0'
    post_full_audio += ' -movflags faststart' # [arg1]
    post_finished_video = '-async 1' # [arg2]


def prepare_rendering_options(scene_name='Scene'):
    '''
    Prepare all of the rendering options from the scene name
    Returns rendering options needed to complete process and
    raises any errors that could come from project rendering
    settings
    '''
    reference_blender_version = (2, 79, 0,)

    def calculate_resolution_percent(scene):
        '''
        Return scaled x and y resolutions
        '''
        res_percent = scene.render.resolution_percentage
        x_resolution = int(res_percent * 0.01 * scene.render.resolution_x)
        y_resolution = int(res_percent * 0.01 * scene.render.resolution_y)

        if x_resolution % 2 != 0  or y_resolution % 2 != 0:
            raise ResolutionNotDivisableException('Resolution is not divisible by 2')

        return x_resolution, y_resolution

    def is_output_loseless(scene):
        if BLENDER_VERSION < reference_blender_version:
            return scene.render.ffmpeg.use_lossless_output
        else:
            if scene.render.ffmpeg.constant_rate_factor == 'LOSSLESS':
                return True
            return False

    for scene in bpy.data.scenes:
        if scene.name == scene_name:
            if scene.render.ffmpeg.use_autosplit:
                error_message = 'Please UNCHECK "AUTOSPLIT OUTPUT" option in the encoding section.'
                LOGGER.fatal(error_message)
                raise UpdateAutoSplitException(error_message)

            resolution = calculate_resolution_percent(scene)
            total_frames = scene.frame_end - scene.frame_start + 1

            LOGGER.debug('%i total frames found in a scene "%s".', total_frames, scene_name)

            if total_frames < CORES_ENABLED:
                error_message = 'Not enough frames for rendering, at least %i needed'
                LOGGER.fatal(error_message, CORES_ENABLED)
                raise NotEnoughFramesException(error_message, CORES_ENABLED)

            loseless = is_output_loseless(scene)

            LOGGER.debug('Scene "%s" uses loseless encoding: %s', scene.name, loseless)

            return RenderingOptions(
                total_frames=total_frames,
                frames_per_second=scene.render.fps,
                start_frame=scene.frame_start,
                end_frame=scene.frame_end,
                x_resolution=resolution[0],
                y_resolution=resolution[1],
                file_format=scene.render.image_settings.file_format,
                video_format=scene.render.ffmpeg.format,
                video_codec=scene.render.ffmpeg.codec
            )

    try:
        for seq in scene.sequence_editor.sequences_all:
            if seq.bl_rna.name == 'Scene Sequence' and scene.name == scene_name:
                if not seq.use_sequence:
                    LOGGER.warning('Scene strips are enabled.')
    except AttributeError:
        LOGGER.fatal('VSE is Empty')
        exit(1)

    try:
        for seq in scene.sequence_editor.sequences_all:
            if seq.bl_rna.name == 'Sound Sequence':
                LOGGER.info('Sound Found')
    except AttributeError:
        LOGGER.fatal('VSE is Empty')
        exit(1)


def take_filter_args():
    argv = sys.argv

    if '--' not in argv:
        argv = []
    else:
        argv = argv[argv.index('--') + 1:]

    usage_text = (
        'Render the scene using multiple instances of Blender'
        ' blender --background --python {} -- [options]'.format(SCRIPT_NAME)
    )

    return argv


def main():
    check_file_exist()
    check_cpu()
    options = take_filter_args()
    import pdb;pdb.set_trace()
    LOGGER.info('Additional filter script arguments: %s', options)
    rendering_options = prepare_rendering_options()
    LOGGER.debug('Rendering options: %s', rendering_options)
    render(rendering_options.start_frame, rendering_options.total_frames, options)

if __name__ == '__main__':
    main()
