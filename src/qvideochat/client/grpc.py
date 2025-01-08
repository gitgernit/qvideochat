import asyncio
import dataclasses
import typing

import grpc
import proto.rooms_pb2
import proto.rooms_pb2_grpc

import qvideochat.core.config


@dataclasses.dataclass(frozen=True)
class TextMessage:
    username: str
    text: str


class RoomInteractor:
    def __init__(
        self,
        username: str,
        room_name: str,
        host: str,
        port: str,
    ) -> None:
        self.username = username
        self.room_name = room_name
        self.host = host
        self.port = port
        self.stream: typing.AsyncIterator | None = None

        self._message_queue: asyncio.Queue[str] = asyncio.Queue()

    async def connect(self) -> None:
        channel = grpc.aio.insecure_channel(f'{self.host}:{self.port}')
        stub = proto.rooms_pb2_grpc.RoomsServiceStub(channel)

        md = [
            ('room_name', self.room_name),
            ('username', self.username),
        ]

        async def send_messages() -> (
            typing.AsyncGenerator[proto.rooms_pb2.RoomMethod, None]
        ):
            while True:
                message_text = await self._message_queue.get()

                request = proto.rooms_pb2.SendMessageRequest(text=message_text)
                room_method = proto.rooms_pb2.RoomMethod(send_message=request)

                yield room_method

        self.stream = stub.JoinRoom(send_messages(), metadata=md)

    async def send_message(self, text: str) -> None:
        await self._message_queue.put(text)

    async def read_messages(self) -> typing.AsyncGenerator[TextMessage, None]:
        async for room_method in self.stream:
            if room_method.HasField('message_received'):
                notification = room_method.message_received
                yield TextMessage(
                    username=notification.username,
                    text=notification.text,
                )


async def create_room(name: str) -> str:
    channel = grpc.aio.insecure_channel(
        f'{qvideochat.core.config.config.GRPC_SERVER_HOST}:{qvideochat.core.config.config.GRPC_SERVER_PORT}',
    )
    stub = proto.rooms_pb2_grpc.RoomsServiceStub(channel)

    request = proto.rooms_pb2.CreateRoomRequest(name=name)
    response = await stub.CreateRoom(request)

    return response.name
