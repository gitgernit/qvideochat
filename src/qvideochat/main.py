import asyncio
import sys

from PyQt6 import QtCore
from PyQt6 import QtWidgets
from qasync import QApplication
from qasync import QEventLoop

from qvideochat.ui.videochat import Videochat


def main() -> None:
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_EnableHighDpiScaling, on=True,
        )

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_UseHighDpiPixmaps, on=True,
        )

    app = QApplication(sys.argv)

    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)

    main_window = Videochat()
    main_window.show()

    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


if __name__ == '__main__':
    sys.excepthook = lambda exctype, value, traceback: sys.__excepthook__(
        exctype, value, traceback,
    )
    main()
