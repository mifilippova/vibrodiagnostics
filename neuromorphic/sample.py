import logging
import numpy as np

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    a = np.array([[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                  [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                  [[0, 0, 0], [1, 0, 1], [0, 0, 0], [0, 0, 0]]])
    n, m, k = a.shape  # 3 3 3
    print(np.argmax(a))
    print(a.shape)

