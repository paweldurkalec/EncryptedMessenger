from session import Session, SessionStatus
import time
import threading
from crypto import gen_key_rsa
from Crypto.PublicKey import RSA


with open('test_public_key.txt', 'rb') as f:
    public_key = RSA.importKey(f.read())

with open('test_private_key.txt', 'rb') as f:
    private_key = RSA.importKey(f.read())

session = Session("PAWEL-PC", private_key)
session.open_broadcast()

while len(session.user_list) < 1:
    time.sleep(1)

time.sleep(5)
session.send_init(session.user_list[0].name, session.user_list[0].address, public_key=public_key)

while session.status != SessionStatus.ESTABLISHED:
    time.sleep(1)

while session.status == SessionStatus.ESTABLISHED:
    print("Podaj tresc wiadomosci do wyslania: ")
    msg = input()
    session.send_text_message(msg)

