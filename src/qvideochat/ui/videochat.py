import PyQt6.QtWidgets


class Videochat(PyQt6.QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Videochat')

        self.central_widget = PyQt6.QtWidgets.QWidget()
        self.layout = PyQt6.QtWidgets.QVBoxLayout()

        self.ping_button = PyQt6.QtWidgets.QPushButton('Ping')
        self.event_list = PyQt6.QtWidgets.QListWidget

        self.setup_ui()
        self.setup_events()

    def setup_ui(self) -> None:
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.layout)

        self.layout.addWidget(self.ping_button)

    def setup_events(self) -> None:
        self.ping_button.clicked.connect(lambda: print('Ping!'))  # noqa
