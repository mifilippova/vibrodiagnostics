from event_filter import EF
from video import load_video
import logging

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    video_name = "C:/Users/filip/vibrodiagnostics/videos/neuromorphic-video/dvs-video.avi"

    frames, fps, width, height = load_video(video_name)

    # convert to optimal ef-frames
    ef = EF(frames)
    ef.iteration()

    # apply PCTM

    # extract vibrations & draw charts


