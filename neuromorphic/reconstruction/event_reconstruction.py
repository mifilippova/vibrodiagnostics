import numpy as np
import cv2
from enum import Enum

INTENSITY_ESTIMATE_PUB_QUEUE_SIZE = 1
EVENT_RETENTION_DURATION = 30

class Filter(Enum):
    GAUSSIAN = 1
    BILATERAL = 2

class High_pass_filter:
    def __init__(self, nh, nh_private):
        self.nh = nh

        # Node Handle (publish_framerate, save_dir, working_dir)
        self.__nh = nh_private
        # self.__
        self.__initialized = False
        self.__event_count_cutoff_freq = np.log(1 - 0.95) / EVENT_RETENTION_DURATION
        self.__contrast_threshold_on_adaptive = 0.1
        self.__contrast_threshold_off_adaptive = -0.1
        self.__t_next_publish = 0.0
        self.__t_next_recalibrate_contrast_thresholds = 0.0
        self.__t_next_log_intensity_update = 0.0

    def eventsCallback(self, dvs_msgs):
        if not self.__initialized:
            self.__initialize_image_states(dvs_msgs.height, dvs_msgs.width)

        if dvs_msgs.events.size() > 0:
            for i in range(dvs_msgs.size()):
                x = dvs_msgs.events[i].x
                y = dvs_msgs.events[i].y
                if 0 < x < dvs_msgs.width and 0 < y < dvs_msgs.height:
                    ts = dvs_msgs.events[i].ts.toSeq()
                    polarity = dvs_msgs.events[i].polarity

                    if self.__adaptive_contrast_threshold:
                        self.__update_leaky_event_count(ts, x, y, polarity)

                    self.__update_log_intensity_state(ts, x, y, polarity)

                    if self.__publish_framerate > 0 and ts > self.__t_next_publish:
                        self.__update_log_intensity_state_global(ts)
                        self.__publish_intensity_estimate(dvs_msgs.events[i].ts)
                        self.__t_next_publish = ts + 1 / self.__publish_framerate

                ts = dvs_msgs.events.back().ts.toSeq()
                if self.__adaptive_contrast_threshold and (ts > self.__t_next_recalibrate_contrast_thresholds):
                    self.__contrast_threshold_recalibraion_frequency = 20.0
                    self.__recalibrate_contrast_thresholds(ts)
                    self.__t_next_recalibrate_contrast_thresholds = ts + 1 / self.__contrast_threshold_recalibraion_frequency

    def set_parameters(self):
        pass

    def __reconfigureCallbacks(self, config, level):
        pass

    def __init_image_states(self, rows, columns):
        pass

    def __update_log_intensity_state(self, ts, x, y, polarity):
        delta_t = ts - self.__ts_array[y, x]
        constant_threshold = 0.0
        if delta_t < 0:
            self.__initialize_image_states(self.__log_intensity_state.rows, self.__log_intensity_state.cols)
            return

        if self.__adaptive_contrast_threshold:
            constant_threshold = self.__contrast_threshold_on_adaptive \
                if polarity else self.__contrast_threshold_off_adaptive

        else:
            constant_threshold = self.__contrast_threshold_on_user_defined \
                if polarity else self.__contrast_threshold_off_user_defined

        self.__log_intensity_state[y, x] = np.exp(
            -self.__cutoff_frequency_global * delta_t - self.__cutoff_frequency_per_event_component
        ) * self.__log_intensity_state[y, x] + constant_threshold
        self.__ts_array[y, x] = ts

    def __update_log_intensity_state_global(self, ts):
        # beta = np.zeros()
        delta_t = ts - self.__ts_array
        min = 0.0
        cv2.minMaxLoc(delta_t, min)
        if min < 0:
            self.__initialize_image_states(self.__log_intensity_state.rows, self.__log_intensity_state.cols)
            return

        beta = cv2.exp(-self.__cutoff_frequency_global * (ts - self.__ts_array))
        self.__ts_array = ts

    def __update_leaky_event_count(self, ts, x, y, polarity):
        if polarity:
            delta_t = (ts - self.__ts_array_on[y, x])
            if delta_t >= 0:
                self.__leaky_event_count_on[y, x] = np.exp(
                    -self.__event_count_cutoff_freq * delta_t
                ) * self.__leaky_event_count_on[y, x] + 1

                self.__ts_array_on[y, x] = ts
            else:
                delta_t = (ts - self.__ts_array_off[y, x])
                if delta_t >= 0:
                    self.__leaky_event_count_off[y, x] = np.exp(
                        -self.__event_count_cutoff_freq * delta_t
                    ) * self.__leaky_event_count_off[y, x] + 1

                    self.__ts_array_off[y, x] = ts

    def __recalibrate_contrast_thresholds(self, ts):
        EVENT_DENSITY_MIN = 5e6
        decay_factor_on = cv2.exp(-self.__event_count_cutoff_freq * (ts - self.__ts_array_on))
        decay_factor_off = cv2.exp(-self.__event_count_cutoff_freq * (ts - self.__ts_array_off))

        self.__leaky_event_count_on *= decay_factor_on
        self.__leaky_event_count_off *= decay_factor_off

        self.__ts_array_on = ts
        self.__ts_array_off = ts

        sum_on = cv2.sum(self.__leaky_event_count_on[0])
        sum_off = cv2.sum(self.__leaky_event_count_off[0])

        if sum_on + sum_off > EVENT_DENSITY_MIN:
            self.__contrast_threshold_off_adaptive = -sum_on / (sum_off + 1e-10) \
                                                     * self.__contrast_threshold_on_adaptive

    def __publish_intensity_estimate(self, ts):
       # display_image
       # cv_image
        self.__convert_log_intensity_state_to_display_image(display_image=None, ts.toSec())

        # cv_image.encoding = "mono8"
        if self.__spatial_filter_sigma > 0:
            if (spatial_smoothing_method == Filter.GAUSSIAN):
                cv2.GaussianBlur() # display_image, filtered_display_image, cv::Size(5, 5), spatial_filter_sigma_, spatial_filter_sigma_
            elif (Filter.BILITERAL):
                biliteral_sigma = self.__spatial_silter_sigma * 25
                # cv2.biliteralFilter(display_image, filtere) display_image, filtered_display_image, 5, bilateral_sigma, bilateral_sigma

            display_image = filtered_display_image

        cv_image.image = display_image
        cv_image.header.stamp = timestamp

        # save image

    def __convert_log_intensity_state_to_display_image(self, display_image, ts):
        pass

    def minMaxLocRobust(self, image, lower_bound, upper_bound, percentage_pixels_to_discard):
        pass

    # void
    # High_pass_filter::minMaxLocRobust(const
    # cv::Mat & image, double * robust_min, double * robust_max,
    # const
    # double & percentage_pixels_to_discard)
    # {
    #     CHECK_NOTNULL(robust_max);
    # CHECK_NOTNULL(robust_min);
    # cv::Mat
    # image_as_row;
    # cv::Mat
    # image_as_row_sorted;
    # const
    # int
    # single_row_idx_min = (0.5 * percentage_pixels_to_discard / 100) * image.total();
    # const
    # int
    # single_row_idx_max = (1 - 0.5 * percentage_pixels_to_discard / 100) * image.total();
    # image_as_row = image.reshape(0, 1);
    # cv::sort(image_as_row, image_as_row_sorted, CV_SORT_EVERY_ROW + CV_SORT_ASCENDING);
    # image_as_row_sorted.convertTo(image_as_row_sorted, CV_64FC1);
    # *robust_min = image_as_row_sorted.at < double > (single_row_idx_min);
    # *robust_max = image_as_row_sorted.at < double > (single_row_idx_max);
    # }
    #
    # void
    # High_pass_filter::reconfigureCallback(pure_event_reconstruction::pure_event_reconstructionConfig & config, uint32_t
    # level)
    # {
    #     cutoff_frequency_global_ = config.Cutoff_frequency * 2 * M_PI;
    # cutoff_frequency_per_event_component_ = config.Cutoff_frequency_per_event_component;
    # contrast_threshold_on_user_defined_ = config.Contrast_threshold_ON;
    # contrast_threshold_off_user_defined_ = config.Contrast_threshold_OFF;
    # intensity_min_user_defined_ = config.Intensity_min;
    # intensity_max_user_defined_ = config.Intensity_max;
    # adaptive_contrast_threshold_ = config.Auto_detect_contrast_thresholds;
    # spatial_filter_sigma_ = config.Spatial_filter_sigma;
    # spatial_smoothing_method_ = int(config.Bilateral_filter);
    # adaptive_dynamic_range_ = config.Auto_adjust_dynamic_range;
    # color_image_ = config.Color_display;
    # }

    def __initialize_image_states(self, height, width):
        self.__log_intensity_state = np.zeros((height, width), dtype="uint8")
        self.__leaky_event_count_on = np.zeros((height, width), dtype="uint8")
        self.__leaky_event_count_off = np.zeros((height, width), dtype="uint8")
        self.__ts_array = np.zeros((height, width), dtype="uint8")
        self.__ts_array_on = np.zeros((height, width), dtype="uint8")
        self.__ts_array_off = np.zeros((height, width), dtype="uint8")

        self.__t_next_publish = 0.0
        self.__t_next_recalibrate_contrast_thresholds = 0.0
        self.__t_next_log_intensity_update = 0.0

        self.__initialised = True
