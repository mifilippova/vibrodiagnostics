from ipywidgets import interact, fixed, interact_manual, FloatSlider, IntSlider
import math
from matplotlib import rc
rc('animation', html='jshtml')
import numpy as np

from utils import Timer, Event, normalize_image, animate, load_events, plot_3d, event_slice

def high_pass_filter(event_data, cutoff_frequency=5):
    print('Reconstructing, please wait...')
    events, height, width = event_data.event_list, event_data.height, event_data.width
    events_per_frame = 2e4
    with Timer('Reconstruction'):
        time_surface = np.zeros((height, width), dtype=np.float32)
        image_state = np.zeros((height, width), dtype=np.float32)
        image_list = []
        for i, e in enumerate(events):
            beta = math.exp(-cutoff_frequency * (e.t - time_surface[e.y, e.x]))
            image_state[e.y, e.x] = beta * image_state[e.y, e.x] + e.p
            time_surface[e.y, e.x] = e.t
            if i % events_per_frame == 0:
                beta = np.exp(-cutoff_frequency * (e.t - time_surface))
                image_state *= beta
                time_surface.fill(e.t)
                image_list.append(np.copy(image_state))
    return animate(image_list, 'High Pass Filter')

def leaky_integrator(event_data, beta=1.0):
    print('Reconstructing, please wait...')
    events, height, width = event_data.event_list, event_data.height, event_data.width
    events_per_frame = 2e4
    with Timer('Reconstruction (simple)'):
        image_state = np.zeros((height, width), dtype=np.float32)
        image_list = []
        for i, e in enumerate(events):
            image_state[e.y, e.x] = beta * image_state[e.y, e.x] + e.p
            if i % events_per_frame == 0:
                image_list.append(np.copy(image_state))
    fig_title = 'Direct Integration' if beta == 1 else 'Leaky Integrator'
    return animate(image_list, fig_title)

interact(event_slice, event_data=fixed(event_data),
         start=FloatSlider(min=0, max=1, step=0.01,continuous_update=False),
         duration_ms=IntSlider(value=50, min=0, max=500, step=1, continuous_update=False))

interact_manual(leaky_integrator, event_data=fixed(event_data), beta=(0, 1, 0.01))

interact_manual(high_pass_filter, event_data=fixed(event_data), cutoff_frequency=(0, 20, 0.01))

def complementary_filter(event_data, cutoff_frequency=5.0):
    print('Reconstructing, please wait...')
    events, height, width = event_data.event_list, event_data.height, event_data.width
    frames, frame_timestamps = event_data.frames, event_data.frame_timestamps
    events_per_frame = 2e4
    with Timer('Reconstruction'):
        time_surface = np.zeros((height, width), dtype=np.float32)
        image_state = np.zeros((height, width), dtype=np.float32)
        image_list = []
        frame_idx = 0
        max_frame_idx = len(frames) - 1
        log_frame = np.log(frames[0] + 1)
        for i, e in enumerate(events):
            if frame_idx < max_frame_idx:
                if e.t >= frame_timestamps[frame_idx + 1]:
                    log_frame = np.log(frames[frame_idx + 1] + 1)
                    frame_idx += 1
            beta = math.exp(-cutoff_frequency * (e.t - time_surface[e.y, e.x]))
            image_state[e.y, e.x] = beta * image_state[e.y, e.x] \
                                    + (1 - beta) * log_frame[e.y, e.x] + 0.1 * e.p
            time_surface[e.y, e.x] = e.t
            if i % events_per_frame == 0:
                beta = np.exp(-cutoff_frequency * (e.t - time_surface))
                image_state = beta * image_state + (1 - beta) * log_frame
                time_surface.fill(e.t)
                image_list.append(np.copy(image_state))
    return animate(image_list, 'Complementary Filter')

interact_manual(complementary_filter, event_data=fixed(event_data), cutoff_frequency=(0, 20, 0.01))
