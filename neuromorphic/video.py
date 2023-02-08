import cv2
import numpy as np
import logging as log


def load_video(name):
    '''
    load video
    :return:
    :param name: filename
    :return: video_list, fps, width, height
    '''

    video = cv2.VideoCapture(name)
    fps = video.get(cv2.CAP_PROP_FPS)
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    video_list = []
    ret = 1
    while ret:
        ret, frame = video.read()
        # TODO: to grayscale, make def if needed
        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            video_list.append(gray_frame)

    video.release()
    log.info(f"Successfully read video file with fps: {fps}, frames: {width} x {height}")
    return np.array(video_list), fps, width, height
