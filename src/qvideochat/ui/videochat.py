import asyncio
import html

import grpc
import PyQt6.QtCore
import PyQt6.QtWidgets
import qasync

import qvideochat.client.grpc
import qvideochat.core.config
from qvideochat.ui.gen.videochat import Ui_QVideoChat


class Videochat(PyQt6.QtWidgets.QWidget, Ui_QVideoChat):
    def __init__(self) -> None:
        super().__init__()

        self.room_interactor: qvideochat.client.grpc.RoomInteractor | None = (
            None
        )
        self._logging_tasks: list[asyncio.Task] = []

        self.setupUi(self)
        self.setup_signals()

    def setup_signals(self) -> None:
        self.create_room_button.clicked.connect(self.create_room)
        self.join_room_button.clicked.connect(self.join_room)
        self.leave_room_button.clicked.connect(self.leave_room)

    @qasync.asyncSlot()
    async def create_room(self) -> None:
        self.create_room_button.setEnabled(False)

        room_name = self.room_creation_name_input.text()
        resulting_room_name = await qvideochat.client.grpc.create_room(
            room_name,
        )

        self.room_name_label.setText(f'Room Name: {resulting_room_name}')
        self.create_room_button.setEnabled(True)

    @qasync.asyncSlot()
    async def join_room(self) -> None:
        username = self.username_input.text()
        room_name = self.room_name_input.text()

        self.room_interactor = qvideochat.client.grpc.RoomInteractor(
            username,
            room_name,
            qvideochat.core.config.config.GRPC_SERVER_HOST,
            qvideochat.core.config.config.GRPC_SERVER_PORT,
        )

        try:
            await self.room_interactor.connect()

        except grpc.RpcError:
            self.room_interactor = None
            return

        self.stackedWidget.setCurrentIndex(1)
        self.inner_room_name_label.setText(f'Room Name: {room_name}')

        task = asyncio.create_task(self.log_messages())
        self._logging_tasks.append(task)

        self.message_input.returnPressed.connect(self.send_message)

    @qasync.asyncSlot()
    async def leave_room(self) -> None:
        self.stackedWidget.setCurrentIndex(0)
        self.message_history.clear()
        self.room_users_list.clear()
        self.message_input.returnPressed.disconnect()

        await self.room_interactor.disconnect()
        self.room_interactor = None

        for task in self._logging_tasks:
            task.cancel()

    @qasync.asyncSlot()
    async def send_message(self) -> None:
        message_text = self.message_input.text()
        await self.room_interactor.send_message(message_text)
        self.message_input.setText('')

    async def log_messages(self) -> None:
        async for message in self.room_interactor.read_messages():
            if isinstance(message, qvideochat.client.grpc.TextMessage):
                escaped_username = html.escape(message.username)
                escaped_text = html.escape(message.text)

                self.message_history.appendPlainText(
                    f'{escaped_username}: {escaped_text}',
                )

            elif isinstance(message, qvideochat.client.grpc.UsersMessage):
                self.room_users_list.clear()
                self.room_users_list.addItems(message.users)
