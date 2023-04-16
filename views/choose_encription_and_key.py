from lazy_import import lazy_module
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Semaphore

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from views.chat_view import ChatView
from stoppable_thread import StoppableThread

wait_for_chat_module = lazy_module('views.wait_for_chat_view')

class ChooseEncriptionAndKey(BasicView):

    def __init__(self, root, private_key, public_key, name, images, session):
        super(ChooseEncriptionAndKey, self).__init__(root, images)
        self.session= session
        self.private_key = private_key
        self.public_key = public_key
        self.name = name
        self.display_widgets()
        self.popup = None
        self.thread = StoppableThread(self.wait_for_other_user)
        self.thread.thread.start()
        self.display_popup()


    def display_widgets(self):
        pass # TODO

    def display_popup(self):
        response = messagebox.askokcancel("Oczekiwanie na użytkownika", "Trwa oczekiwanie na dołączenia użytkownika do czatu")
        if response == 'cancel':
            pass # TODO
        self.popup = None

    def switch_to_chat(self):
        if self.popup:
            self.popup.destroy()
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        ChatView(self.root, self.private_key, self.public_key, self.name, self.images, self.session)


    def switch_to_wait_for_chat(self):
        pass

    def wait_for_other_user(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.ESTABLISHED:
                self.root.after(0, lambda: self.switch_to_chat())