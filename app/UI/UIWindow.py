import time
from multiprocessing import Process, Queue

from PyQt5 import QtMultimedia
from PyQt5.QtCore import QDir, QUrl, QEventLoop
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QMenuBar, QMainWindow, QAction, QFileDialog, QPushButton, \
    QLabel

from app import video
from app.UI.UIElement import UIElement, ParamsDialog, SpecifyCamera, SpecifyMode
from high_speed import alg_video, alg_area
from neuromorphic.event_convertion import EventData


class UIWindow:
    MAIN_WINDOW_OBJECTS = [(QMenuBar, "menubar"), (QVideoWidget, "videoWidget"), (QLabel, "colorbar"),
                           (QLabel, "chart"), (QPushButton, "playButton")]

    def __init__(self):
        self.main_window = UIElement(UIWindow.MAIN_WINDOW_OBJECTS, "app/UI/MainWindow.ui", QMainWindow())
        self.specify_mode_dialog = SpecifyMode("app/UI/SpecifyMode.ui", self.main_window, self)
        self.params_dialog = ParamsDialog("app/UI/ParamsDialog.ui", self.main_window, self)
        self.specify_camera_dialog = SpecifyCamera("app/UI/SpecifyCamera.ui", self.main_window, self)

        self.mediaPlayer = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        self.path = ""
        self.video = None

        self.params_dialog.initialize()
        self.specify_camera_dialog.initialize()
        self.specify_mode_dialog.initialize()

        self.initialize_menubar()

        self.main_window.element.show()

    def initialize_menubar(self):
        self.main_window.element.findChild(QAction, "uploadVideo").triggered.connect(self.upload_video)
        self.main_window.element.findChild(QAction, "exit").triggered.connect(lambda: self.main_window.element.close())

        self.main_window.element.findChild(QAction, "saveReport").triggered.connect(self.save_report)
        self.main_window.element.findChild(QAction, "startAnalysis").triggered.connect(self.start_alg)

        self.main_window.elements["playButton"].clicked.connect(self.play)
        self.mediaPlayer.setVideoOutput(self.main_window.elements["videoWidget"])
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)

    def upload_video(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self.main_window.element, "Открыть видео", QDir.homePath())
        if fileName != '':
            self.path = fileName
            self.video = video.LocalVideo(fileName)
            self.video.load_video()
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.main_window.elements["playButton"].setText("Остановить")
        else:
            self.main_window.elements["playButton"].setText("Запустить")

    def save_report(self):
        pass

    def start_alg(self):
        self.specify_camera_dialog.show()

        if self.main_window.camera == "neuromorphic":
            self.path = EventData.convert_to_intensity(self.path, palette="Grayscale")

        self.specify_mode_dialog.show()

        if self.main_window.mode == "contour":
            self.params_dialog.show()
            alg_video.Algorithm(self.video, self.video.t) # self.first, self.second)

            self.main_window.elements["chart"].setPixmap(
                QPixmap('pic/filled_contours1.jpg').scaledToWidth(self.main_window.elements["chart"].width()))
            self.main_window.elements["colorbar"].setPixmap(
                QPixmap('pic/colorbar1.jpg').scaledToWidth(self.main_window.elements["colorbar"].width()))
        else:
            # start area alg
            self.start_alg_area()

    def start_alg_area(self):
        # alg_area.Algorithm(self.video, self.video.t)
        queue = Queue()
        alg = alg_area.Algorithm(self.video, self.video.t)
        p = Process(target=alg_area.Algorithm.start, args=(alg, alg.t, alg.template, 'magnified_video'))
        p.start()
        p.join()  # this blocks until the process terminates

        self.main_window.elements["chart"].setPixmap(
             QPixmap('pic/magnified_video.jpg'))#.scaledToWidth(400))
