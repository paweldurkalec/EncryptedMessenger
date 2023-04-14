from session import Session
import time
import threading

session = Session("PAWEL-LAPCOK")
session.start()

time.sleep(5)

print(f"Active threads: {threading.active_count()}")

time.sleep(10)

print(f"Active threads: {threading.active_count()}")