import numpy as np
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

import alg_area
import alg_video
import video


class Area(QWidget):
    fileName = ''
    localVideo = None

    def __init__(self):
        super(QWidget, self).__init__()
        self.setWindowTitle("Vibrations Detecting - Area")
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
        self.rectangle = QLabel('')
        self.magnified = QLabel('')

        self.maxMeanText = QLabel('', self)
        self.maxMeanText.setAlignment(Qt.AlignCenter)
        self.maxMeanText.setStyleSheet("background-color : lightgray")
        self.maxMeanText.setFont(QtGui.QFont("Times", 10, weight=QtGui.QFont.Bold))

        self.progressAlgorithm = QProgressBar(self)

        layout = QGridLayout()
        layout.addWidget(self.openButton, 0, 0)
        layout.addWidget(self.playButton, 1, 0)
        layout.addWidget(self.algButton, 2, 0)
        layout.addWidget(self.frame, 3, 0)
        layout.addWidget(self.rectangle, 4, 0)
        layout.addWidget(self.magnified, 4, 1)
        layout.addWidget(self.progressAlgorithm, 5, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.maxMeanText, 5, 1, Qt.AlignmentFlag.AlignBottom)

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
            self.magnified.setPixmap(QPixmap().scaledToWidth(630))
            self.resize(640, 480)
            self.show()

    def play(self):
        if self.fileName != '':
            self.localVideo.play_videoFile()

    def alg(self):
        if self.fileName != '':
            alg_area.Algorithm(self, self.localVideo.t)
            self.magnified.setPixmap(QPixmap('pic/magnified_video.jpg').scaledToWidth(630))

    def setMaxMean(self, value):
        self.maxMeanText.setText(value)

    def setProgressMax(self, value):
        self.progressAlgorithm.setMaximum(value)

    def setProgressValue(self, value):
        self.progressAlgorithm.setValue(value)

    def setRectangle(self):
        self.rectangle.setPixmap(QPixmap('pic/rectangle.jpg').scaledToWidth(630))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    area = Area()
    area.resize(640, 480)
    area.show()
    sys.exit(app.exec_())
