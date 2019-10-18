import math

def rendering_sections(start_frame, total_frames, sections=4):
    portion_of_frames_per_core = math.ceil(total_frames / sections)
    end_frame = start_frame + portion_of_frames_per_core - 1

    result = []

    for section in range(0, sections):
        result.append((start_frame, end_frame))
        start_frame = end_frame + 1
        end_frame += portion_of_frames_per_core
        if end_frame >= total_frames:
          end_frame = total_frames

    return result
