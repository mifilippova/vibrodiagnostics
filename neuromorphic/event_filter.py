import pygad
from scipy.fft import fft2, ifft2
import numpy as np
import logging as log


class EF:
    def __init__(self, frames, k=3):
        '''
        :param frames: original video frames
        :param k: order of EF-filter
        '''
        self.frames = frames
        self.ef_frames = np.empty_like(frames, dtype=complex)
        self.k = k
        self.a = np.ones(k)
        self.b = np.ones(k)

    def generate_ef_frames(self):
        log.info("Start generating EF-frames")

        for t in range(len(self.frames)):
            sum_b = np.zeros_like(self.frames[t], dtype=complex)
            for n in range(min(self.k, t)):
                sum_b += fft2(self.frames[t - n]) * np.complex(self.b[n])

            sum_a = np.zeros_like(self.frames[t], dtype=complex)
            for m in range(1, min(self.k, t)):
                sum_a += fft2(self.frames[t - m]) * np.complex(self.a[m])

            self.ef_frames[t] = sum_b - sum_a

        log.info("EF-frames successfully generated")

    def cross_power_spectrum(self):
        log.info("Start calculating cross-power spectrum")
        deltas = []
        for t in range(1, len(self.ef_frames)):
            r = np.abs(ifft2((self.ef_frames[t - 1] * np.conj(self.ef_frames[t]))
                             / np.abs(self.ef_frames[t - 1] * np.conj(self.ef_frames[t]))))
            _, col = r.shape
            deltas.append(np.array([np.argmax(np.real(r)) // col, np.argmax(np.real(r)) % col]))

        # log.debug(f"First 5 deltas: {deltas}")
        log.info("Cross-power spectrum successfully calculated")
        return np.array(deltas)

    @staticmethod
    def pad_with(vector, pad_width, iaxis, kwargs):
        pad_value = kwargs.get('padder', 0)
        vector[:pad_width[0]] = pad_value
        vector[-pad_width[1]:] = pad_value

    def cost_function(self, deltas, K=2, m=2):
        log.info("Start calculating cost function")
        den = 0
        for n in range(1, len(self.ef_frames)):
            i_max, j_max = deltas[n - 1]
            # in case i_max, j_max are on borders
            temp_frame = np.pad(self.ef_frames[n], m, self.pad_with)
            i_max += m
            j_max += m
            den = np.sum(temp_frame[i_max - m:i_max + m, j_max - m:j_max + m]) / self.ef_frames[n][i_max - m, j_max - m]

        nValid = 0
        for n in range(len(self.ef_frames) - 1):
            i_max, j_max = deltas[n]
            nValid += 1 if self.ef_frames[n][i_max, j_max] - self.ef_frames[n + 1][i_max, j_max] > K else 0
        log.debug(f"# of valid frames: {nValid}")

        cost = 1 / den + len(self.frames) / nValid

        log.info("Cost function successfully calculated")
        return np.real(cost)

    def iteration(self):
        self.generate_ef_frames()
        deltas = self.cross_power_spectrum()
        cost = self.cost_function(deltas)
        log.debug(f"Cost function = {cost}")