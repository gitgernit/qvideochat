import asyncio
import dataclasses
import typing

import grpc
import proto.rooms_pb2
import proto.rooms_pb2_grpc

import qvideochat.core.config


class Message:
    pass


@dataclasses.dataclass(frozen=True)
class TextMessage(Message):
    username: str
    text: str


@dataclasses.dataclass(frozen=True)
class UsersMessage(Message):
    users: list[str]


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
        self.stream: (asyncio.Future | typing.AsyncIterator) | None = None

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
        await asyncio.sleep(0.15)  # this sucks but grpc api spares no one

        if (
            self.stream.done()
            and await self.stream.code() != grpc.StatusCode.OK
        ):
            error_message = await self.stream.details()
            raise grpc.RpcError(
                grpc.StatusCode.INVALID_ARGUMENT, error_message,
            )

    async def disconnect(self) -> None:
        if self.stream is not None:
            self.stream.cancel()
            self.stream = None

    async def send_message(self, text: str) -> None:
        await self._message_queue.put(text)

    async def read_messages(self) -> typing.AsyncGenerator[Message, None]:
        async for room_method in self.stream:
            if room_method.HasField('message_received'):
                notification = room_method.message_received
                yield TextMessage(
                    username=notification.username,
                    text=notification.text,
                )

            elif room_method.HasField('room_users'):
                notification = room_method.room_users
                yield UsersMessage(
                    users=[user.username for user in notification.users],
                )


async def create_room(name: str) -> str:
    channel = grpc.aio.insecure_channel(
        f'{qvideochat.core.config.config.GRPC_SERVER_HOST}:{qvideochat.core.config.config.GRPC_SERVER_PORT}',
    )
    stub = proto.rooms_pb2_grpc.RoomsServiceStub(channel)

    request = proto.rooms_pb2.CreateRoomRequest(name=name)
    response = await stub.CreateRoom(request)

    return response.name
