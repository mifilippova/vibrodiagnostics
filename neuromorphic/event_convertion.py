import numpy as np
import cv2


class EventData:
    def __init__(self, event_video, palette="Grayscale"):

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

        video.release()

        self.event_list = np.array(video_list)
        self.event_list_raw = np.array(video_list_raw)
        self.width = width
        self.height = height
        self.fps = fps

    def high_pass_filter(self):
        int_img_list = []
        lg_int_est = np.zeros(shape=(int(self.height), int(self.width)), dtype=np.float32)
        t_est = 0

        alpha = 2 * np.pi  # as in paper

        min_int = 0
        max_int = 0
        c = 0.1

        # for each event on frame and frame
        for i, frame in enumerate(self.event_list):
            t = i * 1.0 / self.fps
            delta_t = t - t_est
            lg_int_est = np.exp(-alpha * delta_t) * lg_int_est

            # recalibrate contrast threshold
            sum_on = np.sum(np.abs(lg_int_est[frame == 255]))
            sum_off = np.sum(lg_int_est[frame == 0])

            if sum_on + sum_off > 5e6:
                c = -sum_on / (sum_off + 1e-10) * c
                # print(f"i: {i}, c: {c}")

            # for all events in frame
            lg_int_est[frame == 255] += c  # positive
            lg_int_est[frame == 0] -= c  # negative

            int_img_list.append(lg_int_est)
            min_int = min(np.min(lg_int_est), min_int)
            max_int = max(np.max(lg_int_est), max_int)

            # update time
            t_est = t

        return np.array(int_img_list), min_int, max_int

    def save_video(self, path, img_list, mini, maxi):
        def lg_to_its(x):
            return np.exp(x)

        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), \
                              self.fps, (int(self.width), int(self.height)))

        li = np.vectorize(lg_to_its)

        for i, img in enumerate(img_list):
            fr = np.empty_like(self.event_list_raw[0])
            # img = np.uint8(255 * normalize_image(img, mini, maxi))
            img = np.uint8(255 * self.normalize_image(li(img), li(mini), li(maxi)))
            # img = cv2.GaussianBlur(img, (3, 3), 3)
            fr[:, :, 0] = img
            fr[:, :, 1] = img
            fr[:, :, 2] = img

            out.write(fr)

        out.release()

    @staticmethod
    def convert_to_intensity(path, palette="Grayscale"):
        event_data = EventData(path, palette=palette)
        imgs, mini, maxi = event_data.high_pass_filter()
        save_path = path[:-3] + "_nrmf" + path[-3:]
        print(f"Intensity video saved to {save_path}")
        event_data.save_video(save_path, imgs, mini, maxi)
        return save_path

    @staticmethod
    def normalize_image(image, mini, maxi):
        # mini, maxi = np.percentile(image, (percentile_lower, percentile_upper))

        if mini == maxi:
            return 0 * image + 0.5  # gray image
        # return np.clip((image - mini) / (maxi - mini + 1e-5), 0, 1)
        return (image - mini) / (maxi - mini)
