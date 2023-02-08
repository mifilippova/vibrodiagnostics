from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

import app_area
import app_cont


class Mode(QMainWindow):

    def __init__(self):
        super(QMainWindow, self).__init__()
        self.area = None
        self.cont = None
        self.setWindowTitle("Vibrations Detecting")
        self.setStyleSheet("background-color: white;")

        self.contMode = QPushButton('Contours Mode')
        self.contMode.setStyleSheet("background-color : lightgray")
        self.contMode.clicked.connect(self.start_cont)

        self.areaMode = QPushButton('Area Mode')
        self.areaMode.setStyleSheet("background-color : lightgray")
        self.areaMode.clicked.connect(self.start_area)

        self.example1 = QLabel('')
        self.example1.setPixmap(QPixmap('pic/example1.jpg').scaledToWidth(300))
        self.example2 = QLabel('')
        self.example2.setPixmap(QPixmap('pic/example2.jpg').scaledToWidth(300))

        widget = QWidget(self)
        self.setCentralWidget(widget)

        layout = QGridLayout()
        layout.addWidget(self.contMode, 0, 0)
        layout.addWidget(self.areaMode, 0, 1)
        layout.addWidget(self.example1, 1, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.example2, 1, 1, Qt.AlignmentFlag.AlignTop)

        widget.setLayout(layout)

    def start_cont(self):
        self.cont = app_cont.Contours()
        self.cont.clearAll()
        self.cont.resize(640, 480)
        self.cont.show()

    def start_area(self):
        self.area = app_area.Area()
        self.area.clearAll()
        self.area.resize(640, 480)
        self.area.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mode = Mode()
    mode.resize(640, 250)
    mode.show()
    sys.exit(app.exec())
