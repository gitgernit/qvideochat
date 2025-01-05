import sys

import PyQt6.QtWidgets

from qvideochat.ui.videochat import Videochat


def main() -> None:
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    videochat = Videochat()
    videochat.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
