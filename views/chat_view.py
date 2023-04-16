from lazy_import import lazy_module
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Semaphore

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from stoppable_thread import StoppableThread

wait_for_chat_module = lazy_module('views.wait_for_chat_view')

class ChatView(BasicView):

    MY_COLOR = '#ADD8E6'
    CONNECTED_USER_COLOR = '#90EE90'

    def __init__(self, root, private_key, public_key, name, images, session):
        super(ChatView, self).__init__(root, images)
        self.name = name
        self.session = session
        self.public_key = public_key
        self.private_key = private_key
        self.place_for_text_messages = None
        self.text_input = None
        self.displayed_messages = []
        self.semaphore = Semaphore(1)
        self.display_widgets()
        self.thread = StoppableThread(self.chat_with_connected_user)
        self.thread.thread.start()



    def display_widgets(self):
        self.place_for_text_messages = tk.Text(self.root)
        self.place_for_text_messages.place(x=20, y=50, width=300, height=400)
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.config(command=self.place_for_text_messages.yview)
        scrollbar.place(x=320, y=50)
        self.place_for_text_messages.config(yscrollcommand=scrollbar.set)
        self.text_input = tk.Entry(self.root, width=40)
        self.text_input.place(x=20, y=500)
        send_button = tk.Button(self.root, text='Wyslij', command=self.send_message)
        send_button.place(x =300, y=500)
        tk.Button(self.root, text="Zamknij czat", command=self.switch_to_wait_for_chat).place(x=0,y=0)


    def switch_to_wait_for_chat(self):
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        wait_for_chat_module.WaitForChatView(self.root, self.private_key, self.public_key, self.name, self.images)

    def send_message(self):
        text = self.text_input.get()
        self.text_input.delete(0, len(text))
        self.display_message(text, self.MY_COLOR)
        self.session.send_text_message(text)

    def chat_with_connected_user(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.UNESTABLISHED:
                return # dont know what to do
            messages = self.session.text_messages
            if self.displayed_messages != messages:
                self.semaphore.acquire()
                for i in range(len(self.displayed_messages), len(messages)):
                    self.display_message(messages[i], self.CONNECTED_USER_COLOR)
                self.semaphore.release()
                self.displayed_messages = messages.copy()

    def display_message(self, text, color):
        self.place_for_text_messages.tag_configure(color, background=color)
        self.place_for_text_messages.insert(tk.END, text + '\n', color)
        self.root.update()




