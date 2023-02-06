import cv2
import matplotlib.pyplot as plt
import numpy as np


class Algorithm:
    t = None
    video_player = None

    def __init__(self, video_player, t):
        self.t = t.copy()
        self.video_player = video_player
        template = self.get_template(t)
        self.video_player.setRectangle()
        self.start(t, template, 'magnified_video')

    def template_mathing(self, temp, pic2):
        # to gray image
        temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
        pic2 = cv2.cvtColor(pic2, cv2.COLOR_BGR2GRAY)
        w, h = temp.shape[::-1]

        img = pic2.copy()
        method = 'cv2.TM_CCORR_NORMED'
        method = eval(method)
        # Apply template Matching
        res = cv2.matchTemplate(img, temp, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        cv2.rectangle(img, top_left, bottom_right, 255, 2)
        return top_left, bottom_right

    def dist(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    # строим график колебаний точки
    def start(self, t, temp, name):
        centers = []
        self.video_player.setProgressMax(len(t) - 2 - 1)
        # проходим по всем кадрам
        for i in range(len(t) - 2):

            # обновляем прогресс
            self.video_player.setProgressValue(i)


            # находим расположение нашей области
            top_left, bottom_right = self.template_mathing(temp, t[i + 1])
            # запоминаем, где центр фигуры
            centers.append([top_left[1] + 0.5 * (bottom_right[1] - top_left[1]),
                            top_left[0] + 0.5 * (bottom_right[0] - top_left[0])])
        # находим дистанцию между точками центров
        centers_differences = [self.dist(centers[i + 1][0], centers[i + 1][1], centers[i][0], centers[i][1])
                               for i in range(len(centers) - 1)]
        # убираем ошибки template mathcing
        centers_differences = [item if item < 100 else 0
                               for item in centers_differences]

        plt.clf()
        plt.subplots()
        plt.plot(range(1, len(centers)), centers_differences)
        #plt.title(name)
        plt.xlabel('Frames')
        plt.ylabel('Distance in pixels')
        plt.savefig('pic/' + name + '.jpg')

        self.video_player.setMaxMean(f'max = {np.max(centers_differences)}, mean = {np.mean(centers_differences)}')


    # функция для того, чтобы определить область, которую будем отслеживать
    def get_template(self, t):
        temp = Template(t[0].copy())
        top_left_corner, bottom_right_corner = temp.get_area()
        return t[0][top_left_corner[1]:bottom_right_corner[1], top_left_corner[0]:bottom_right_corner[0]]


# Класс для выбора области, которую надо отследить (template то есть)
class Template:
    image = None
    top_left_corner = None
    bottom_right_corner = None

    def __init__(self, image):
        self.image = image

    def draw_rectangle(self, action, x, y, flags, *userdata):
        if action == cv2.EVENT_LBUTTONDOWN:
            self.top_left_corner = (x, y)
        elif action == cv2.EVENT_LBUTTONUP:
            self.bottom_right_corner = (x, y)
            # Draw the rectangle
            cv2.rectangle(self.image, self.top_left_corner, self.bottom_right_corner, (0, 255, 0), 2, 8)
            cv2.imshow("Area choice", self.image)
            cv2.waitKey(0)
            return

    def get_area(self):

        cv2.namedWindow("Area choice")
        cv2.setMouseCallback("Area choice", self.draw_rectangle)
        while (self.top_left_corner is None) or (self.bottom_right_corner is None):
            # Display the image
            cv2.imshow("Area choice", self.image)
            cv2.waitKey(0)

        #cv2.imshow("Chosen area", self.image)
        #cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite('pic/rectangle.jpg', self.image.copy())
        return self.top_left_corner, self.bottom_right_corner
