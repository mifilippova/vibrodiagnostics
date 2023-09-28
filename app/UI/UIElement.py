from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QRadioButton, QPushButton, QLineEdit


class UIElement:
    def __init__(self, elements, ui_path, element_type):
        self.element = element_type
        uic.loadUi(ui_path, self.element)
        self.elements = dict()
        for element in elements:
            self.elements[element[1]] = self.element.findChild(element[0], element[1])
        self.camera = "highspeed"
        self.mode = "area"
        self.first = 10.0
        self.second = 50.0


class ParamsDialog(UIElement):
    OBJECTS = [(QLineEdit, "paramFirstValue"), (QLineEdit, "paramSecondValue"), (QPushButton, "confirm")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(ParamsDialog.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["confirm"].clicked.connect(self.get_params)

    def get_params(self):
        self.first = float(self.elements["paramFirstValue"].text())
        self.second = float(self.elements["paramSecondValue"].text())

    def show(self):
        self.first.setText("0.0")
        self.second.setText("0.0")
        self.element.setWindowModality(Qt.ApplicationModal)
        self.element.exec_()


class SpecifyCamera(UIElement):
    OBJECTS = [(QRadioButton, "highspeed"), (QRadioButton, "neuromorphic"), (QPushButton, "confirm")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(SpecifyCamera.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["highspeed"].setChecked(False)
        self.elements["neuromorphic"].setChecked(False)
        self.elements["highspeed"].toggled.connect(lambda: self.neuromorphic_selected)
        self.elements["confirm"].clicked.connect(self.element.hide)

    def neuromorphic_selected(self):
        self.parent.camera = "neuromorphic"
        self.element.hide()

    def show(self):
        self.elements["highspeed"].setChecked(False)
        self.elements["neuromorphic"].setChecked(False)
        self.element.setWindowModality(Qt.ApplicationModal)
        self.element.exec_()


class SpecifyMode(UIElement):
    OBJECTS = [(QPushButton, "areaModeButton"), (QPushButton, "contourModeButton")]

    def __init__(self, ui_path, parent, ui):
        self.parent = parent
        self.ui = ui
        super().__init__(SpecifyMode.OBJECTS, ui_path, QDialog(self.parent.element))

    def initialize(self):
        self.elements["areaModeButton"].clicked.connect(self.start_area_alg)
        self.elements["contourModeButton"].clicked.connect(self.start_cont_alg)

    def start_area_alg(self):
        self.parent.mode = "area"
        self.element.hide()

    def start_cont_alg(self):
        self.parent.mode = "contour"
        self.element.close()

    def show(self):
        self.element.setWindowModality(Qt.ApplicationModal)
        self.element.exec_()
