import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import alg_video
import video


class Contours(QWidget):
    fileName = ''
    localVideo = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibrations Detecting - Contours")
        self.setStyleSheet("background-color: white;")

        self.playButton = QPushButton('Play Video')
        self.playButton.setStyleSheet("background-color : lightgray")
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.algButton = QPushButton('Start Algorithm')
        self.algButton.setStyleSheet("background-color : lightgray")
        self.algButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.algButton.clicked.connect(self.alg)

        self.openButton = QPushButton("Open new video")
        self.openButton.setStyleSheet("background-color : lightgray")
        self.openButton.clicked.connect(self.openFile)

        self.frame = QLabel('')
        self.canny = QLabel('')
        self.filledContours = QLabel('')
        self.colorbar = QLabel('')

        self.progressAlgorithm = QProgressBar(self)

        #widget = QWidget(self)
        #self.setCentralWidget(widget)

        layout = QGridLayout()
        layout.addWidget(self.openButton, 0, 0)
        layout.addWidget(self.playButton, 1, 0)
        layout.addWidget(self.algButton, 2, 0)
        layout.addWidget(self.frame, 3, 0)
        layout.addWidget(self.canny, 4, 0)
        layout.addWidget(self.filledContours, 4, 1)
        layout.addWidget(self.progressAlgorithm, 5, 0)
        layout.addWidget(self.colorbar, 5, 1)

        #widget.setLayout(layout)
        self.setLayout(layout)

    def openFile(self):
        # сброс
        self.clearAll()

        self.fileName, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())
        if self.fileName != '':
            self.localVideo = video.LocalVideo(self.fileName)
            self.localVideo.load_video()
            self.frame.setPixmap(QPixmap('pic/first_frame.jpg').scaledToWidth(630))

    def clearAll(self):
        if self.fileName != '':
            self.destroy()
            self.__init__()

            self.resize(640, 480)
            self.show()

    def play(self):
        if self.fileName != '':
            self.localVideo.play_videoFile()

    def alg(self):
        if self.fileName != '':
            alg_video.Algorithm(self, self.localVideo.t)
            self.canny.setPixmap(QPixmap('pic/canny.jpg').scaledToWidth(630))
            self.filledContours.setPixmap(QPixmap('pic/filled_contours.jpg').scaledToWidth(630))
            self.colorbar.setPixmap(QPixmap('pic/colorbar.jpg').scaledToWidth(630))

    def setProgressMax(self, value):
        self.progressAlgorithm.setMaximum(value)

    def setProgressValue(self, value):
        self.progressAlgorithm.setValue(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    cont = Contours()
    cont.resize(640, 480)
    cont.show()
    sys.exit(app.exec_())
