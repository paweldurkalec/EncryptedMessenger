import socket
import struct
import time
import utils
import datetime
from frames import FrameType, FrameFactory
from enum import IntEnum
from stoppable_thread import StoppableThread
from user_info import UserInfo

DEBUG = True
BROADCAST_INTERVAL = 5
SOCKET_TIMEOUT = 3
INIT_FRAME_TIMEOUT = 30
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
CONNECTION_PORT = 5008


class SessionStatus(IntEnum):
    NEW = 0,
    UNESTABLISHED = 1,
    WAITING_FOR_RESPONSE = 2,
    WAITING_FOR_ACCEPTANCE = 3,
    ESTABLISHED = 4


class Session:

    def __init__(self, user_name, mcast_grp=MCAST_GRP, mcast_port=MCAST_PORT):
        self.status = SessionStatus.NEW
        self.user_list = []
        self.info = {"user_name": user_name, "mcast_grp": mcast_grp, "mcast_port": mcast_port}
        self.connected_user = None
        self.text_messages = []
        self.file_messages = []
        self.send_broadcast_thread = StoppableThread(self.send_broadcast)
        self.listen_broadcast_thread = StoppableThread(self.listen_for_broadcasts)
        self.listen_connection_thread = StoppableThread(self.listen_for_connections)
        self.listen_frames_thread = StoppableThread(self.listen_for_frames)
        self.init_connection_thread = None
        self.init_frame_reciv_time = None

    def open_broadcast(self):
        self.user_list = []
        self.status = SessionStatus.UNESTABLISHED
        self.send_broadcast_thread.thread.start()
        self.listen_broadcast_thread.thread.start()
        self.listen_connection_thread.thread.start()

    def close_broadcast(self):
        self.send_broadcast_thread.stop()
        self.listen_broadcast_thread.stop()
        self.listen_connection_thread.stop()

    def send_broadcast(self, stop_event, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        frame = FrameFactory.create_frame(FrameType.READY_TO_CONNECT, sender_name=self.info["user_name"])

        while not stop_event.is_set():
            utils.send_frame(sock, frame, protocol="UDP", info=self.info)
            time.sleep(BROADCAST_INTERVAL)

    def listen_for_broadcasts(self, stop_event, **kwargs):
        multicast_group = self.info["mcast_grp"]
        server_address = ('', self.info["mcast_port"])

        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind to the server address
        sock.bind(server_address)

        # Tell the operating system to add the socket to the multicast group
        # on all interfaces.
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(SOCKET_TIMEOUT)

        while not stop_event.is_set():
            frame, address = utils.get_frame(sock, stop_event, protocol="UDP")
            if frame is not None:
                user = UserInfo(frame.sender_name, address)
                if user not in self.user_list and user.address != socket.gethostbyname(socket.gethostname()):
                    self.user_list.append(UserInfo(frame.sender_name, address))

    def listen_for_connections(self, stop_event, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', CONNECTION_PORT))
        sock.listen(5)
        sock.settimeout(3)

        while not stop_event.is_set():
            try:
                client_sock, conn_info = sock.accept()
                others_address = conn_info[0]
                print(f"Connection from {others_address}")
            except TimeoutError:
                continue
            if utils.address_present(self.user_list, others_address):
                self.connected_user = UserInfo("Unknown", others_address, client_sock)
                self.listen_frames_thread.thread.start()
                if DEBUG:
                    print(f"Connection from {others_address} has been established!")

    def listen_for_frames(self, stop_event):
        while not stop_event.is_set():
            frame = utils.get_frame(self.connected_user.client_sock, stop_event, "TCP")
            if frame is not None:
                self.handle_frame(frame, stop_event)

    def handle_frame(self, frame, stop_event):
        if frame.frame_type == FrameType.INIT_CONNECTION and self.status == SessionStatus.UNESTABLISHED:
            if DEBUG:
                print("Got init frame")
            self.connected_user.name = frame.sender_name
            self.init_frame_reciv_time = datetime.datetime.now()
            self.status = SessionStatus.WAITING_FOR_ACCEPTANCE

        elif frame.frame_type == FrameType.ACCEPT_CONNECTION and self.status == SessionStatus.WAITING_FOR_ACCEPTANCE:
            if frame.response == "ACCEPT":
                self.status = SessionStatus.ESTABLISHED
                if DEBUG:
                    print("Got acceptance, status established")
            else:
                self.status = SessionStatus.UNESTABLISHED
                self.connected_user = None
                stop_event.set()
                return

    def send_init_func(self, stop_event, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(kwargs["address"])
        sock.connect((kwargs["address"], CONNECTION_PORT))
        sock.settimeout(INIT_FRAME_TIMEOUT + 2)

        frame = FrameFactory.create_frame(FrameType.INIT_CONNECTION, sender_name=self.info["user_name"],
                                          block_cipher="X", block_size="X", key_size="X", session_key="X",
                                          initial_vector="X")

        utils.send_frame(sock, frame)
        self.status = SessionStatus.WAITING_FOR_RESPONSE
        self.connected_user = UserInfo(kwargs["name"], kwargs["address"], sock)
        self.listen_frames_thread.thread.start()

        if DEBUG:
            print("Init frame sent")

    def send_init(self, name, address):
        self.init_connection_thread = StoppableThread(self.send_init_func, name=name, address=address)
        self.init_connection_thread.thread.start()

    # TODO: what if second person calls stop_waiting_for_response?
    def accept(self):
        if self.status != SessionStatus.WAITING_FOR_ACCEPTANCE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_ACCEPTANCE")

        if datetime.datetime.now() - datetime.timedelta(seconds=INIT_FRAME_TIMEOUT) > self.init_frame_reciv_time:
            self.status = SessionStatus.UNESTABLISHED
            raise TimeoutError("Init frame expired")

        frame = FrameFactory.create_frame(FrameType.ACCEPT_CONNECTION, mac="X", response="ACCEPT")
        utils.send_frame(self.connected_user.sock, frame)
        self.close_broadcast()
        self.status = SessionStatus.ESTABLISHED

    def decline(self):
        if self.status != SessionStatus.WAITING_FOR_ACCEPTANCE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_ACCEPTANCE")

        frame = FrameFactory.create_frame(FrameType.ACCEPT_CONNECTION, mac="X", response="DECLINE")
        utils.send_frame(self.connected_user.sock, frame)
        self.status = SessionStatus.UNESTABLISHED

    def stop_waiting_for_response(self):
        if self.status != SessionStatus.WAITING_FOR_RESPONSE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_RESPONSE")

        self.status = SessionStatus.UNESTABLISHED
        self.listen_frames_thread.stop()
        self.connected_user = None
