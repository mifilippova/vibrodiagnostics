import sys

import PyQt5

from app.UI.UIWindow import UIWindow


class Application():
    def __init__(self, args):
        args.append("--disable-web-security")
        self.app = PyQt5.QtWidgets.QApplication(args)
        self.window = UIWindow()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = Application(sys.argv)
    app.run()