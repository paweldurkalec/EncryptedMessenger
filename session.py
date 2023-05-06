import socket
import struct
import time
import utils
import datetime
import crypto
from frames import FrameType, FrameFactory, Frame
from enum import IntEnum
from stoppable_thread import StoppableThread
from user_info import UserInfo
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES


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

    def __init__(self, user_name, private_key, mcast_grp=MCAST_GRP, mcast_port=MCAST_PORT):
        self.status = SessionStatus.NEW
        self.user_list = []
        self.info = {"user_name": user_name, "mcast_grp": mcast_grp, "mcast_port": mcast_port}
        self.connected_user = None
        self.cipher_info = {
            "symmetric_key_len": 0,
            "block_cipher": "",
            "session_key": bytes(),
            "initial_vector": bytes(),
            "public_key": bytes(),
            "private_key": private_key
        }
        self.text_messages = []
        self.file_messages = []
        self.send_broadcast_thread = StoppableThread(self.send_broadcast)
        self.listen_broadcast_thread = StoppableThread(self.listen_for_broadcasts)
        self.listen_connection_thread = StoppableThread(self.listen_for_connections)
        self.listen_frames_thread = StoppableThread(self.listen_for_frames)
        self.init_frame_create_time = None

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
        print("sending broadcast")
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
                if user not in self.user_list and user.address != socket.gethostbyname(socket.gethostname()) and user.name != self.info['user_name']:
                    print("found user")
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
            except TimeoutError:
                continue
            if utils.address_present(self.user_list, others_address):
                self.connected_user = UserInfo("Unknown", others_address, client_sock)
                self.listen_frames_thread.thread.start()
                if DEBUG:
                    print(f"Connection from {others_address} has been established!")

    def listen_for_frames(self, stop_event):
        while not stop_event.is_set():
            frame = utils.get_frame(self.connected_user.sock, stop_event, "TCP")
            if frame is not None and isinstance(frame, Frame):
                if DEBUG:
                    print("got frame")
                self.handle_frame(frame, stop_event)
            else:
                self.status = SessionStatus.UNESTABLISHED
                self.connected_user = None
                self.listen_frames_thread.stop()
                print("Init timeouted")
        print("listen for frames stopped")

    def handle_frame(self, frame, stop_event):
        self.decrypt_frame(frame)
        if frame.frame_type == FrameType.INIT_CONNECTION and self.status == SessionStatus.UNESTABLISHED:
            if DEBUG:
                print("Got init frame")
            self.connected_user.name = frame.sender_name
            self.init_frame_create_time = datetime.datetime.now()
            self.cipher_info["symmetric_key_len"] = frame.key_size
            self.cipher_info["block_cipher"] = frame.block_cipher
            self.cipher_info["session_key"] = frame.session_key
            self.cipher_info["initial_vector"] = frame.initial_vector
            self.status = SessionStatus.WAITING_FOR_ACCEPTANCE

        elif frame.frame_type == FrameType.ACCEPT_CONNECTION and self.status == SessionStatus.WAITING_FOR_RESPONSE:
            if frame.response == "ACCEPT":
                self.status = SessionStatus.ESTABLISHED
                if DEBUG:
                    print("Got acceptance, status established")
            else:
                self.status = SessionStatus.UNESTABLISHED
                self.connected_user = None
                self.listen_frames_thread.stop()
                return

        elif frame.frame_type == FrameType.TEXT_MESSAGE and self.status == SessionStatus.ESTABLISHED:
            self.text_messages.append(frame.text)

    def send_init(self, name, address, public_key="X", block_cipher="CBC", symmetric_key_len=128):
        if symmetric_key_len != 128 and symmetric_key_len != 192 and symmetric_key_len != 256:
            raise ValueError('AES key length should be equal to 128 or 192 or 256')

        session_key = get_random_bytes(symmetric_key_len // 8)
        initial_vector = get_random_bytes(AES.block_size)

        self.cipher_info["symmetric_key_len"] = symmetric_key_len
        self.cipher_info["block_cipher"] = block_cipher
        self.cipher_info["public_key"] = public_key
        self.cipher_info["session_key"] = session_key
        self.cipher_info["initial_vector"] = initial_vector

        frame = FrameFactory.create_frame(FrameType.INIT_CONNECTION, sender_name=self.info["user_name"],
                                          block_cipher=self.cipher_info["block_cipher"],
                                          key_size=self.cipher_info["symmetric_key_len"], session_key=session_key,
                                          initial_vector=initial_vector)

        self.encrypt_frame(frame)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, CONNECTION_PORT))
        sock.settimeout(INIT_FRAME_TIMEOUT + 2)
        utils.send_frame(sock, frame)
        #self.init_frame_create_time = datetime.datetime.now()
        #self.init_handle_timeout_thread.thread.start()

        self.status = SessionStatus.WAITING_FOR_RESPONSE
        self.connected_user = UserInfo(name, address, sock)
        self.listen_frames_thread.thread.start()

        if DEBUG:
            print("Init frame sent")

    # TODO: what if second person calls stop_waiting_for_response?
    def accept(self, public_key):
        if self.status != SessionStatus.WAITING_FOR_ACCEPTANCE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_ACCEPTANCE")

        if datetime.datetime.now() - datetime.timedelta(seconds=INIT_FRAME_TIMEOUT) > self.init_frame_create_time:
            self.status = SessionStatus.UNESTABLISHED
            self.connected_user = None
            self.listen_frames_thread.stop()
            print("Init frame expired")
            return

        self.cipher_info["public_key"] = public_key
        frame = FrameFactory.create_frame(FrameType.ACCEPT_CONNECTION, response="ACCEPT")
        utils.send_frame(self.connected_user.sock, frame)
        self.close_broadcast()
        self.status = SessionStatus.ESTABLISHED

    def decline(self):
        if self.status != SessionStatus.WAITING_FOR_ACCEPTANCE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_ACCEPTANCE")

        if not (datetime.datetime.now() - datetime.timedelta(seconds=INIT_FRAME_TIMEOUT) > self.init_frame_create_time):
            frame = FrameFactory.create_frame(FrameType.ACCEPT_CONNECTION, response="DECLINE")
            utils.send_frame(self.connected_user.sock, frame)

        self.status = SessionStatus.UNESTABLISHED
        self.connected_user = None
        self.listen_frames_thread.stop()

    def stop_waiting_for_response(self):
        if self.status != SessionStatus.WAITING_FOR_RESPONSE:
            raise Exception(f"Status is {self.status} instead of WAITING_FOR_RESPONSE")

        self.status = SessionStatus.UNESTABLISHED
        self.listen_frames_thread.stop()
        self.connected_user = None

    def send_text_message(self, msg):
        frame = FrameFactory.create_frame(FrameType.TEXT_MESSAGE, text=msg)
        self.encrypt_frame(frame)
        utils.send_frame(self.connected_user.sock, frame)

    def encrypt_frame(self, frame):
        if frame.frame_type == FrameType.TEXT_MESSAGE:
            frame.text = crypto.encrypt_aes(frame.text, self.cipher_info)

        elif frame.frame_type == FrameType.INIT_CONNECTION:
            frame.session_key = crypto.encrypt_rsa(frame.session_key, self.cipher_info["public_key"])

    def decrypt_frame(self, frame):
        if frame.frame_type == FrameType.TEXT_MESSAGE:
            frame.text = crypto.decrypt_aes(frame.text, self.cipher_info)

        elif frame.frame_type == FrameType.INIT_CONNECTION:
            frame.session_key = crypto.decrypt_rsa(frame.session_key, self.cipher_info["private_key"])



