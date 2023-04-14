from threading import Thread, Event


class StoppableThread:

    def __init__(self, func, **kwargs):
        self.stop_event = Event()
        self.func = func
        self.kwargs = kwargs
        self.thread = Thread(target=func, args=[self.stop_event], kwargs=kwargs)

    def stop(self):
        self.stop_event.set()
        self.stop_event = Event()
        self.thread = Thread(target=self.func, args=[self.stop_event], kwargs=self.kwargs)