from session import Session, SessionStatus
import time
import threading

session = Session("PAWEL-PC")
session.open_broadcast()

while len(session.user_list) < 1:
    time.sleep(1)

time.sleep(5)
session.send_init(session.user_list[0].name, session.user_list[0].address)

if session.status == SessionStatus.ESTABLISHED:
    print("Podaj tresc wiadomosci do wyslania: ")
    msg = input()
    session.send_text_message(msg)
