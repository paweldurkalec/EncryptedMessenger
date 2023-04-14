from threading import Thread, Event


class StoppableThread:

    def __init__(self, func, **kwargs):
        self.stop_event = Event()
        self.thread = Thread(target=func, args=[self.stop_event], kwargs=kwargs)

    def stop(self):
        self.stop_event.set()