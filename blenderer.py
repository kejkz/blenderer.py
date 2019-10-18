import os
import bpy
import sys
import argparse
import logging
import multiprocessing
import subprocess
import math
import tempfile
from typing import NamedTuple, List
from collections import namedtuple
import time
import json
import traceback

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
        'y_resolution',
        'render_filepath'
    ]
)

class InputFileNotProvided(Exception):
    pass


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
SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.dirname(bpy.data.filepath)
RENDERING_VERBOSITY_LEVEL = 0

BLENDER_VERSION = check_blender_version()
BLENDER_EXEC_PATH = bpy.app.binary_path
BLENDER_FILE_PATH = os.path.join(ROOT_PATH, bpy.path.basename(bpy.context.blend_data.filepath))
BLENDER_ENGINE = 'BLENDER_RENDER'
VIDEO_EXTENSION = 'mp4'
CONCAT_VIDEO_FILE_NAME = 'concat_video_list.txt'

AUDIO_MIXRATES = ('44100', '48000', '96000', '192000', )
BLENDER_IMAGE_FORMATS = (
    'BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA',
    'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EX', 'HDR', 'TIFF', )

TEMP_DIR = tempfile.TemporaryDirectory(prefix='renderer')


def check_file_exist():
    if not BLENDER_FILE_PATH:
        raise InputFileNotProvided('No blender input file provided... Exiting...')


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
    else:
        return ''


def render_command(filepath: str, start_frame: int, end_frame: int, output_file_path: str) -> str:
    '''
    Creates a blender render command for all of the platforms.
    If an empty list of filtering options is provided, this command
    doesn't include filtering script into the rendering pipeline
    '''
    return [
        BLENDER_EXEC_PATH, '-b', filepath,
        '-s', str(start_frame), '-e', str(end_frame),
        '-o', output_file_path,
        '--verbose', str(RENDERING_VERBOSITY_LEVEL), '-a']


def merge_command(concat_file_path, output_file_path):
    '''Merge temporary video output files'''
    return 'ffmpeg -f concat -safe 0 -y -i {} -c copy {} -loglevel panic'.format(concat_file_path, output_file_path)


def temp_video_file_path(core, start_frame, end_frame):
    output_filename = os.path.join(
        TEMP_DIR.name,
        '{}_{}-{}.{}'.format(core, start_frame, end_frame, VIDEO_EXTENSION))
    return output_filename


def call_render_commands(render_commands, verbose=False):
    if verbose:
        stdout = subprocess.STDOUT
    else:
        stdout = subprocess.DEVNULL
    processes = [subprocess.Popen(comm, stdout=stdout, stderr=subprocess.STDOUT) for comm in render_commands]
    exit_codes = [p.wait() for p in processes]

    if 1 in exit_codes:
        raise BlenderRenderingError('Something went wrong with one of the rendering subprocesses')


def render(blender_file_path: str, render_options: RenderingOptions) -> None:
    video_sections = utils.rendering_sections(
        render_options.start_frame,
        render_options.total_frames,
        CORES_ENABLED
    )

    concat_video_list_path = os.path.join(TEMP_DIR.name, CONCAT_VIDEO_FILE_NAME)
    concat_file_paths = []
    render_commands = []

    for core, section in enumerate(video_sections, start=1):
        output_file_path = temp_video_file_path(core, section[0], section[1])
        command = render_command(blender_file_path, section[0], section[1], output_file_path)
        LOGGER.debug('Render command:\n %s', ' '.join(command))
        render_commands.append(command)
        concat_file_paths.append(output_file_path)

    with open(concat_video_list_path, 'w') as f:
        for video in concat_file_paths:
            f.write("file '{}'\n".format(video))

    call_render_commands(render_commands)

    merge_video_files_command = merge_command(concat_video_list_path, render_options.render_filepath)

    LOGGER.debug(merge_video_files_command)

    try:
        output = subprocess.check_output(
            merge_video_files_command, stderr=subprocess.STDOUT, shell=True, timeout=3, universal_newlines=True)
    except subprocess.CalledProcessError as exc:
        LOGGER.fatal("Command FAIL: %s", exc.output)
        LOGGER.fatal("Command exit status code: %s", exc.returncode)
        exit(1)
    else:
        LOGGER.debug("Command SUCCESS: %s", output)
        LOGGER.info('Output file created at %s', render_options.render_filepath)

    TEMP_DIR.cleanup()


def check_cpu_count():
    if CORES_ENABLED == 1:
        LOGGER.warning('%s script utilizes multiple logical cores, and this system have only 1', SCRIPT_NAME)
        return
    LOGGER.info('Utilizing %i cores', CORES_ENABLED)


def audio_options():
    post_full_audio = '-c:v copy -c:a copy -map 0:v:0 -map 1:a:0'
    post_full_audio += ' -movflags faststart' # [arg1]
    post_finished_video = '-async 1' # [arg2]


def prepare_rendering_options(scene_name='Scene', render_filepath=None):
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

    def is_output_lossless(scene):
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

            if render_filepath == None:
                render_filepath = bpy.path.abspath(scene.render.filepath)

            LOGGER.debug('%i total frames found in a scene "%s".', total_frames, scene_name)

            if total_frames < CORES_ENABLED:
                error_message = 'Not enough frames for rendering, at least %i needed'
                LOGGER.fatal(error_message, CORES_ENABLED)
                raise NotEnoughFramesException(error_message, CORES_ENABLED)

            lossless = is_output_lossless(scene)

            LOGGER.debug('Scene "%s" uses lossless encoding: %s', scene.name, lossless)

            return RenderingOptions(
                total_frames=total_frames,
                frames_per_second=scene.render.fps,
                start_frame=scene.frame_start,
                end_frame=scene.frame_end,
                x_resolution=resolution[0],
                y_resolution=resolution[1],
                file_format=scene.render.image_settings.file_format,
                video_format=scene.render.ffmpeg.format,
                video_codec=scene.render.ffmpeg.codec,
                render_filepath=render_filepath
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

    parser.add_argument('-so', '--scene-options', type=json.loads, help='Scene rendering options as JSON')
    parser.add_argument('-ro', '--render-output', type=str, help='Rendering output file location')
    parser.add_argument('-ird', '--images-root-dir', type=str, help='Images root directory', default=None)

    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    return args


def save_temp_blender_file() -> str:
    '''Save current blend file to a temporary location before rendering'''
    tempfile_path = os.path.join(TEMP_DIR.name, bpy.path.basename(BLENDER_FILE_PATH))
    bpy.ops.wm.save_as_mainfile(filepath=tempfile_path)
    return tempfile_path


def main():
    start_time =  time.time()
    try:
        check_file_exist()
        check_cpu_count()
        script_arguments = parse_optional_args()

        if script_arguments:
            rendering_options = prepare_rendering_options(
                render_filepath=script_arguments.render_output)
            LOGGER.debug('Rendering options: %s', rendering_options)
            if script_arguments.scene_options or script_arguments.images_root_dir:
                LOGGER.info('Additional filter script arguments: %s', script_arguments)
                LOGGER.info('Prepare rendering using filter options...')
                filterer.SceneModifier(
                    script_arguments.scene_options,
                    script_arguments.images_root_dir
                ).alter_scene()
                LOGGER.info('Scene has been modified...')
                LOGGER.info('Save current blender scene to a temp file...')
                blender_file_path = save_temp_blender_file()
                LOGGER.info('Temp file saved as: {}'.format(blender_file_path))
            else:
                blender_file_path = BLENDER_FILE_PATH
                LOGGER.info('Rendering file: {}'.format(blender_file_path))
        else:
            LOGGER.debug('No script arguments provided')
            rendering_options = prepare_rendering_options()
            blender_file_path = BLENDER_FILE_PATH
        render(blender_file_path, rendering_options)
        LOGGER.info('Rendering took %.2f seconds.', time.time() - start_time)
    except (InputFileNotProvided, BlenderRenderingError) as err:
        LOGGER.fatal(err)
        exit(1)


if __name__ == '__main__' and __package__ is None:
    try:
        sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))
        import filterer
        import utils
        main()
    except Exception as exc:
        LOGGER.fatal(traceback.format_exc())
        LOGGER.fatal(exc)
        exit(1)
