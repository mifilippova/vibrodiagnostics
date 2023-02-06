import cv2
import numpy as np


class LocalVideo:
    name = ''
    t = None
    fps = None
    width = None
    height = None

    def __init__(self, name):
        self.name = name

    def load_video(self):
        video = cv2.VideoCapture(self.name)
        self.fps = video.get(cv2.CAP_PROP_FPS)
        self.width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        video_list = []
        ret = 1
        while ret:
            ret, frame = video.read()
            video_list.append(frame)

        video.release()
        self.t = np.array(video_list, dtype=object)

        cv2.imwrite('pic/first_frame.jpg', self.t[0])
        cv2.waitKey(0)

    def play_videoFile(self):

        cv2.namedWindow('Video Playing', cv2.WINDOW_AUTOSIZE)
        for frame in self.t[:-1]:
            cv2.imshow('Video Playing', frame)

            if cv2.waitKey(100) == 27:
                break  # esc to quit

        cv2.destroyAllWindows()