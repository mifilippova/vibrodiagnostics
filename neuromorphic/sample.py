import logging
import numpy as np
import math
import cv2
from matplotlib.animation import ArtistAnimation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from os.path import join
import pandas as pd
import time


class EventData:
    def __init__(self, event_video):

        video = cv2.VideoCapture(event_video)
        fps = video.get(cv2.CAP_PROP_FPS)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        video_list = []
        video_list_raw = []
        ret = 1
        while ret:
            ret, frame = video.read()
            if ret:
                # convert from dark pallete map to gray colors
                # 128 - background
                # 255 - positive
                # 0 - negative
                video_list_raw.append(frame)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                mask_background = cv2.inRange(frame, np.array([20, 27, 42]), np.array([40, 47, 62]))
                mask_positive = cv2.inRange(frame, np.array([245, 245, 245]), np.array([255, 255, 255]))
                mask_negative = cv2.inRange(frame, np.array([4, 66, 140]), np.array([104, 166, 255]))

                frame[mask_background > 0] = 128
                frame[mask_positive > 0] = 255
                frame[mask_negative > 0] = 0

                video_list.append(frame[:, :, 0])

        video.release()

        self.event_list = np.array(video_list)
        self.event_list_raw = np.array(video_list_raw)
        self.width = width
        self.height = height
        self.fps = fps


def complementary_filter(event_data):
    int_img_list = []
    # print((event_data.height, event_data.width))
    lg_int_est = np.zeros(shape=(int(event_data.height), int(event_data.width)), dtype=np.float32)
    t_est = 0

    alpha = 2 * np.pi  # as in paper

    # for each event on frame and frame => just 2 in 1
    for i, frame in enumerate(event_data.event_list):
        t = i * 1.0 / event_data.fps
        delta_t = t - t_est
        lg_int_est = np.exp(-alpha * delta_t) * lg_int_est
        # for all events in frame
        lg_int_est[frame == 255] += 0.1  # positive
        lg_int_est[frame == 0] -= 0.1  # negative

        int_img_list.append(lg_int_est)

        # TODO: update alpha

        # update time
        t_est = t

    return int_img_list


def save_video(event_data, img_list):
    # cap = cv2.VideoCapture("output1.avi")
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')

    out = cv2.VideoWriter('gray.avi', fourcc,
                          event_data.fps, (int(event_data.width), int(event_data.height)))

    for i, img in enumerate(img_list):
        img = np.uint8(255 * img)
        cv2.imwrite(f"imgs/{i}.png", img)

        out.write(img)

    out.release()

# Convertion from event data into grayscale video
if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    path = "C:/Users/vibrodiagnostics/videos/neuromorphic-videos/output1.avi"
    event_data = EventData(path)

    imgs = complementary_filter(event_data)

    save_video(event_data, imgs)
