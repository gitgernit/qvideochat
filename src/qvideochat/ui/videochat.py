import PyQt6.QtWidgets

from qvideochat.ui.gen.videochat import Ui_QVideoChat
from qasync import asyncSlot
from qvideochat.core.config import config

import proto.rooms_pb2_grpc
import proto.rooms_pb2

import grpc


class Videochat(PyQt6.QtWidgets.QWidget, Ui_QVideoChat):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setup_signals()

    def setup_signals(self):
        self.create_room_button.clicked.connect(self.create_room)

    @asyncSlot()
    async def create_room(self) -> None:
        self.create_room_button.setEnabled(False)

        channel = grpc.aio.insecure_channel('%s:%s' % (config.GRPC_SERVER_HOST, config.GRPC_SERVER_PORT,))
        stub = proto.rooms_pb2_grpc.RoomsServiceStub(channel)

        request = proto.rooms_pb2.CreateRoomRequest()
        response = await stub.CreateRoom(request)

        self.room_id_label.setText(f'Room ID: {response.id}')

        self.create_room_button.setEnabled(True)
