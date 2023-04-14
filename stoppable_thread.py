from threading import Thread, Event


class StoppableThread:

    def __init__(self, func):
        self.stop_event = Event()
        self.thread = Thread(target=func, args=[self.stop_event])

    def stop(self):
        self.stop_event.set()