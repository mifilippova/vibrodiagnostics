# importing libraries
import cv2
import numpy as np

from colour import Color
import matplotlib.pyplot as plt
import matplotlib as mpl


class Algorithm:
    t = None
    video_player = None

    def __init__(self, video_player, t):
        self.t = t.copy()
        self.video_player = video_player
        centers, contours = self.edge_detection(self.t[0].copy())
        centers_differences_total = self.start2(self.t, contours)
        # mode is 'Picture' or 'Video'

        self.fill_vibrations_contours(self.t, centers_differences_total)

    def template_mathing(self, temp, pic2):
        # to gray image
        temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
        pic2 = cv2.cvtColor(pic2, cv2.COLOR_BGR2GRAY)
        w, h = temp.shape[::-1]

        img = pic2.copy()
        method = 'cv2.TM_CCORR_NORMED'
        method = eval(method)
        # template Matching
        res = cv2.matchTemplate(img, temp, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        return top_left, bottom_right

    def dist(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def edge_detection(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        # Canny Edge Detection
        tr1 = 100
        tr2 = 250
        edges = cv2.Canny(image=img_blur, threshold1=tr1, threshold2=tr2, L2gradient=True)

        # Display Canny Edge Detection Image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        contours = cv2.findContours(closed.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        centers = []
        for cont in contours:
            cv2.drawContours(img, [cont], -1, (0, 255, 0), 4)
            M = cv2.moments(cont)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                centers.append((cx, cy))

        cv2.imwrite('pic/canny.jpg', img)
        # cv2.imshow('result', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return centers, contours

    def start2(self, t, contours):

        centers_differences_total = []

        self.video_player.setProgressMax(len(contours) - 1)

        # проходим по контурам
        for cont_num in range(len(contours)):

            # обновляем прогресс
            self.video_player.setProgressValue(cont_num)

            if len(contours[cont_num]) < 200:
                continue

            centers = []
            cont = contours[cont_num]

            coord1 = np.array(cont).T[0].max()
            coord2 = np.array(cont).T[1].max()
            coord3 = np.array(cont).T[0].min()
            coord4 = np.array(cont).T[1].min()
            temp = t[0][coord4:coord2, coord3:coord1]

            # проходим по всем кадрам
            for i in range(len(t) - 2):
                # находим расположение нашей области
                top_left, bottom_right = self.template_mathing(temp, t[i + 1])
                # запоминаем, где центр фигуры
                centers.append([top_left[1] + 0.5 * (bottom_right[1] - top_left[1]),
                                top_left[0] + 0.5 * (bottom_right[0] - top_left[0])])
            # находим дистанцию между точками центров
            centers_differences = [self.dist(centers[j + 1][0], centers[j + 1][1], centers[j][0], centers[j][1])
                                   for j in range(len(centers) - 1)]
            # убираем ошибки template mathcing
            centers_differences = [item if item < 50 else 0
                                   for item in centers_differences]
            centers_differences_total.append([cont, centers_differences, np.mean(centers_differences)])

        return centers_differences_total

    def sort_key(self, lst):
        return lst[2]

    def fill_vibrations_contours(self, t, centers_differences_total):
        img = t[0].copy()
        centers_differences_total.sort(key=self.sort_key)
        cont = np.array(centers_differences_total, dtype=object).T[0]
        max_diff = centers_differences_total[-1][2]
        min_diff = centers_differences_total[0][2]
        red = Color("red")
        colors = list(red.range_to(Color("green"), 100))
        colors_rgb = [(colors[ind1].rgb[2] * 255, colors[ind1].rgb[0] * 255, colors[ind1].rgb[1] * 255)
                      for ind1 in range(len(colors))]

        for ind in range(len(cont)):
            col_ind = int(100 * (centers_differences_total[ind][2] - min_diff) / (max_diff - min_diff))
            if col_ind == 100:
                col_ind = 99
            cv2.drawContours(img, [cont[ind]], -1, colors_rgb[col_ind], thickness=cv2.FILLED)
        cv2.imwrite('pic/filled_contours.jpg', img)

        # colorbar image
        # colors_reversed = list(Color("green").range_to(red, 100))
        # colors_rgb_reversed = [colors_reversed[ind1].rgb for ind1 in range(len(colors_reversed))]
        colors_rgb_reversed = [(colors_rgb[ind1][1] / 255, colors_rgb[ind1][2] / 255, colors_rgb[ind1][0] / 255)
                               for ind1 in reversed(range(len(colors_rgb)))]
        fig, ax = plt.subplots(figsize=(21, 3))
        fig.subplots_adjust(bottom=0.5)
        cmap = mpl.colors.ListedColormap(colors_rgb_reversed, N=100)
        norm = mpl.colors.Normalize(vmin=min_diff, vmax=max_diff)
        clb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax,
                           orientation='horizontal')
        clb.set_label(label='Pixels', size=30)
        clb.ax.tick_params(labelsize=30)

        fig.savefig('pic/colorbar.jpg')
