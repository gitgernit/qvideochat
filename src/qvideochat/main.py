import sys

import PyQt6.QtWidgets
from PyQt6 import QtCore, QtWidgets

from qvideochat.ui.videochat import Videochat


def main() -> None:
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = PyQt6.QtWidgets.QApplication(sys.argv)
    videochat = Videochat()
    videochat.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
