from user_info import UserInfo
from frames import FrameFactory
from threading import Event


HEADER_SIZE = 10


def address_present(user_list, address):
    for user in user_list:
        if user.address == address:
            return True
    return False


def send_frame(sock, frame, protocol="TCP", info=None):
    if protocol not in ["TCP", "UDP"]:
        raise Exception("Unknown protocol")
    if protocol == "UDP" and info is None:
        raise Exception("Info not provided with UDP protocol")

    msg = FrameFactory.serialize(frame)
    msg = bytes(f'{len(msg):<{HEADER_SIZE}}', "utf-8") + msg
    if protocol=="UDP":
        sock.sendto(msg, (info["mcast_grp"], info["mcast_port"]))
    else:
        sock.send(msg)

def get_frame(sock, stop_event=None, protocol="TCP"):
    if protocol not in ["TCP", "UDP"]:
        raise Exception("Unknown protocol")

    if stop_event is None:
        stop_event = Event()

    full_msg = b''
    new_msg = True
    msg_len = 0

    while not stop_event.is_set():
        try:
            if protocol == "UDP":
                msg, addr = sock.recvfrom(1024)
            elif protocol == "TCP":
                msg = sock.recv(1024)
        except TimeoutError:
            msg, addr = None, None
        if msg is not None:
            if new_msg:
                try:
                    msg_len = int(msg[:HEADER_SIZE])
                    new_msg = False
                except ValueError:
                    print("Got corrupted frame or something that is not a frame")
                    return None, None

            full_msg += msg

            if len(full_msg) - HEADER_SIZE == msg_len:
                frame = FrameFactory.deserialize(full_msg[HEADER_SIZE:])
                if protocol == "UDP":
                    return frame, addr[0]
                elif protocol == "TCP":
                    return frame
        else:
            return None, None



