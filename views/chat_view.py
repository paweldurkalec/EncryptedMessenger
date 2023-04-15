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

    MY_COLOR = 'blue'
    CONNECTED_USER_COLOR = 'green'

    def __init__(self, root, private_key, public_key, name, images, session):
        super(ChatView, self).__init__(root, images)
        self.name = name
        self.session = session
        self.public_key = public_key
        self.private_key = private_key
        self.place_for_text_messages = None
        self.text_input = None
        self.display_widgets()
        self.thread = StoppableThread()
        self.displayed_messages = []
        self.semaphore = Semaphore(1)


    def display_widgets(self):
        self.label = tk.Label(self.root, font=self.MAX_FONT, text="Wiadomości tekstowe").place(0,0)
        self.place_for_text_messages = tk.Frame(self.root, width=300, height=300)
        self.place_for_text_messages.place(x=10, y=50)
        canvas1 = tk.Canvas(self.place_for_text_messages)
        canvas1.pack(side="left", fill="both", expand=True)
        scrollbar1 = tk.Scrollbar(self.place_for_text_messages, orient="vertical", command=canvas1.yview)
        scrollbar1.pack(side="right", fill="y")
        canvas1.configure(yscrollcommand=scrollbar1.set)
        canvas1.bind("<Configure>", lambda e: canvas1.configure(scrollregion=canvas1.bbox("all")))
        inner_frame1 = tk.Frame(canvas1, bg="#EEE")
        canvas1.create_window((0, 0), window=inner_frame1, anchor="nw")
        self.text_input = tk.Entry(self.root, width=50)
        self.place(x=10, y=500)
        send_button = tk.Button(self.root, text='Wyslij')
        send_button.place(x =200, y=500)
        close_chat_button = tk.Button(self.root, text="Zamknij czat", command=self.switch_to_wait_for_chat)

    def switch_to_wait_for_chat(self):
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        wait_for_chat_module.WaitForChatView(self.root, self.private_key, self.public_key, self.name, self.images)

    def send_message(self):
        text = self.text_input.get()
        self.session.send_text_message(text)
        self.text_input.set('')
        self.display_message(text, self.MY_COLOR)

    def chat_with_connected_user(self):
        if self.session.status == SessionStatus.UNESTABLISHED:
            return # dont know what to do
        messages = self.session.text_messages
        if self.displayed_messages != messages:
            self.semaphore.acquire()
            for i in range(len(self.displayed_messages), len(messages)):
                self.display_message(messages[i], self.CONNECTED_USER_COLOR)
            self.semaphore.release()

    def display_message(self, text, color):
        tk.Label(self.place_for_text_messages, text="text", bg=color).pack()



