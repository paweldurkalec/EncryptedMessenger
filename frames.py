from enum import IntEnum
from abc import ABC, abstractmethod
from pickle import dumps, loads


class FrameType(IntEnum):
    READY_TO_CONNECT = 0,
    INIT_CONNECTION = 1,
    ACCEPT_CONNECTION = 2,
    TEXT_MESSAGE = 3,
    FILE_MESSAGE = 4,
    FILE_RESPOND = 5,
    END_SESSION = 6


class Frame(ABC):

    def __init__(self, frame_type):
        self.frame_type = frame_type

    def get_type(self):
        return self.frame_type


# only frame that goes through UDP
class ReadyFrame(Frame):

    def __init__(self, **kwargs):
        super().__init__(FrameType.READY_TO_CONNECT)
        self.sender_name = kwargs.get("sender_name")


class InitFrame(Frame):

    def __init__(self, **kwargs):
        super().__init__(FrameType.INIT_CONNECTION)
        self.sender_name = kwargs.get("sender_name")
        self.block_cipher = kwargs.get("block_cipher")
        self.key_size = kwargs.get("key_size")
        self.session_key = kwargs.get("session_key")
        self.initial_vector = kwargs.get("initial_vector")


class AcceptFrame(Frame):

    def __init__(self, **kwargs):
        super().__init__(FrameType.ACCEPT_CONNECTION)
        self.response = kwargs.get("response") # ACCEPT / DECLINE


class TextMessageFrame(Frame):

    def __init__(self, **kwargs):
        super().__init__(FrameType.TEXT_MESSAGE)
        self.text = kwargs.get("text")


class FileMessageFrame(Frame):

    def __init__(self, **kwargs):
        super().__init__(FrameType.FILE_MESSAGE)
        self.file_name = kwargs.get("file_name")
        self.file_size = kwargs.get("file_size")
        self.frame_number = kwargs.get("frame_number")
        self.content = kwargs.get("content")


class FileRespondFrame(Frame):

    def __init__(self):
        super().__init__(FrameType.FILE_RESPOND)


class EndFrame(Frame):

    def __init__(self):
        super().__init__(FrameType.END_SESSION)


class FrameFactory:

    @staticmethod
    def deserialize(frame):
        return loads(frame)

    @staticmethod
    def serialize(frame):
        return dumps(frame)

    @staticmethod
    def create_frame(frame_type, **kwargs):
        if frame_type not in iter(FrameType):
            raise Exception("Unknown frame type")

        try:
            match frame_type:
                case FrameType.READY_TO_CONNECT:
                    result = ReadyFrame(**kwargs)
                case FrameType.INIT_CONNECTION:
                    result = InitFrame(**kwargs)
                case FrameType.ACCEPT_CONNECTION:
                    result = AcceptFrame(**kwargs)
                case FrameType.TEXT_MESSAGE:
                    result = TextMessageFrame(**kwargs)
                case FrameType.FILE_MESSAGE:
                    result = FileMessageFrame(**kwargs)
                case FrameType.FILE_RESPOND:
                    result = FileRespondFrame(**kwargs)
                case FrameType.END_SESSION:
                    result = EndFrame()
        except Exception as e:
            raise Exception(f"Wrong set of arguments, {e}")

        return result
