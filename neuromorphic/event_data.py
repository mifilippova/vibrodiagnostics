import cv2
import numpy as np


class EventData:
    def __init__(self, event_video, palette="grey"):

        video = cv2.VideoCapture(event_video)
        fps = video.get(cv2.CAP_PROP_FPS)
        width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

        video_list = []
        video_list_raw = []
        ret = 1
        while ret:
            ret, frame = video.read()
            # print(frame)
            if ret:

                # convert from dark pallete map to gray colors for darkpallete
                # 128 - background
                # 255 - positive
                # 0 - negative
                video_list_raw.append(frame)

                if palette == "DarkPalette":
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    mask_background = cv2.inRange(frame, np.array([20, 27, 42]), np.array([40, 47, 62]))
                    mask_positive = cv2.inRange(frame, np.array([245, 245, 245]), np.array([255, 255, 255]))
                    mask_negative = cv2.inRange(frame, np.array([4, 66, 140]), np.array([104, 166, 255]))

                    frame[mask_background > 0] = 128
                    frame[mask_positive > 0] = 255
                    frame[mask_negative > 0] = 0

                    video_list.append(frame[:, :, 0])

                elif palette == "Grayscale":
                    # for gray pallete
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    mask_background = cv2.inRange(frame, np.array([118, 118, 118]), np.array([138, 138, 138]))
                    mask_positive = cv2.inRange(frame, np.array([245, 245, 245]), np.array([255, 255, 255]))
                    mask_negative = cv2.inRange(frame, np.array([0, 0, 0]), np.array([20, 20, 20]))

                    frame[mask_background > 0] = 128
                    frame[mask_positive > 0] = 255
                    frame[mask_negative > 0] = 0

                    video_list.append(frame[:, :, 0])

                else:
                    print("Undefined palette")
                    # TODO: Throw exception

        video.release()

        self.event_list = np.array(video_list)
        self.event_list_raw = np.array(video_list_raw)
        self.width = width
        self.height = height
        self.fps = fps

    def complementary_filter(self):
        int_img_list = []
        # print((event_data.height, event_data.width))
        lg_int_est = np.zeros(shape=(int(self.height), int(self.width)), dtype=np.float32)
        t_est = 0

        alpha = 2 * np.pi  # as in paper

        min_int = 0
        max_int = 0
        # for each event on frame and frame => just 2 in 1
        for i, frame in enumerate(self.event_list):
            t = i * 1.0 / self.fps
            delta_t = t - t_est
            lg_int_est = np.exp(-alpha * delta_t) * lg_int_est
            # for all events in frame
            lg_int_est[frame == 255] += 0.1  # positive
            lg_int_est[frame == 0] -= 0.1  # negative

            int_img_list.append(lg_int_est)
            min_int = min(np.min(lg_int_est), min_int)
            max_int = max(np.max(lg_int_est), max_int)

            # update time
            t_est = t

        return np.array(int_img_list), min_int, max_int

    @staticmethod
    def normalize_image(image, mini, maxi):
        # mini, maxi = np.percentile(image, (percentile_lower, percentile_upper))

        if mini == maxi:
            return 0 * image + 0.5  # gray image
        # return np.clip((image - mini) / (maxi - mini + 1e-5), 0, 1)
        return (image - mini) / (maxi - mini)

    def save_video(self, path, img_list, mini, maxi):

        def lg_to_its(x):
            return np.exp(x)

        # cap = cv2.VideoCapture("output1.avi")
        imgs, min_int, max_int = self.complementary_filter()

        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), \
                              self.fps, (int(self.width), int(self.height)))

        print("Start writing into .avi")
        li = np.vectorize(lg_to_its)

        for i, img in enumerate(img_list):
            fr = np.empty_like(self.event_list_raw[0])
            # img = np.uint8(255 * normalize_image(img, mini, maxi))
            img = np.uint8(255 * self.normalize_image(li(img), li(mini), li(maxi)))
            fr[:, :, 0] = img
            fr[:, :, 1] = img
            fr[:, :, 2] = img

            out.write(fr)

        print("Saved")

        out.release()
