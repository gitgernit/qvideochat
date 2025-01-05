import asyncio

import PyQt6.QtWidgets
from qvideochat.ui.gen.videochat import Ui_QVideoChat
from qasync import asyncSlot


class Videochat(PyQt6.QtWidgets.QWidget, Ui_QVideoChat):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
