from lazy_import import lazy_module
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Semaphore
import os

from session import SessionStatus
from views.basic_view import BasicView
from stoppable_thread import StoppableThread

wait_for_chat_module = lazy_module('views.wait_for_chat_view')


class ChatView(BasicView):

    MY_COLOR = '#ADD8E6'
    CONNECTED_USER_COLOR = '#90EE90'

    def __init__(self, root, private_key, name, images, session, public_keys, private_keys):
        super(ChatView, self).__init__(root, images, public_keys, private_keys)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.name = name
        self.session = session
        self.private_key = private_key
        self.place_for_text_messages = None
        self.place_for_file_messages = None
        self.progress_bar = None
        self.text_input = None
        self.displayed_text_messages = []
        self.displayed_file_messages = []
        self.semaphore = Semaphore(1)
        self.display_widgets()
        self.thread = StoppableThread(self.chat_with_connected_user)
        self.thread.thread.start()

    def on_closing(self):
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć program?"):

            self.thread.stop()
            self.root.destroy()

    def display_widgets(self):
        self.place_for_text_messages = tk.Text(self.root)
        self.place_for_text_messages.place(x=20, y=50, width=300, height=400)
        self.place_for_file_messages = tk.Text(self.root)
        self.place_for_file_messages.place(x=400, y=50, width=200, height=400)
        scrollbar_text = tk.Scrollbar(self.root)
        scrollbar_text.config(command=self.place_for_text_messages.yview)
        scrollbar_text.place(x=320, y=50)
        self.place_for_text_messages.config(yscrollcommand=scrollbar_text.set)
        scrollbar_file = tk.Scrollbar(self.root)
        scrollbar_file.config(command=self.place_for_text_messages.yview)
        scrollbar_file.place(x=320, y=50)
        self.place_for_file_messages.config(yscrollcommand=scrollbar_file.set)
        self.text_input = tk.Entry(self.root, width=40)
        self.text_input.place(x=20, y=500)
        send_button = tk.Button(self.root, text='Wyslij', command=self.send_message)
        send_button.place(x=300, y=500)
        choose_file_button = tk.Button(self.root, font=self.BUTTON_FONT, text="Wybierz plik", command=self.choose_file,width=40)
        choose_file_button.place(x=400,y=500)
        send_file_button = tk.Button(self.root, text='Wyslij', command=self.send_file)
        send_file_button.place(x=500, y=500)
        tk.Button(self.root, text="Zamknij czat", command=self.switch_to_wait_for_chat).place(x=0,y=0)



    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if self.file_label:
                self.file_label.destroy()
            filename = os.path.basename(file_path)
            self.file_label = tk.Label(self.root, text=filename, font=self.BUTTON_FONT,
                                           background=self.BACKGROUND_COLOR)
            self.file_label.place(400,530)

    def switch_to_wait_for_chat(self):
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        wait_for_chat_module.WaitForChatView(self.root, self.private_key, self.public_key, self.name, self.images)

    def send_text_message(self):
        text = self.text_input.get()
        self.text_input.delete(0, len(text))
        self.semaphore.acquire()
        self.display_message(text, self.MY_COLOR)
        self.semaphore.release()
        self.session.send_text_message(text)

    def send_file(self):
        text = self.text_input.get()
        self.text_input.delete(0, len(text))
        self.semaphore.acquire()
        self.display_message(text, self.MY_COLOR)
        self.semaphore.release()
        self.session.send_text_message(text)

    def chat_with_connected_user(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.UNESTABLISHED:
                return self.switch_to_wait_for_chat()
            text_messages = self.session.text_messages
            file_messages = self.session.file_messages
            if self.displayed_text_messages != text_messages:
                self.semaphore.acquire()
                for i in range(len(self.displayed_text_messages), len(text_messages)):
                    self.display_message(text_messages[i], self.CONNECTED_USER_COLOR)
                self.semaphore.release()
                self.displayed_file_messages = text_messages.copy()
            if self.displayed_file_messages != file_messages:
                self.semaphore.acquire()
                for i in range(len(self.displayed_file_messages), len(file_messages)):
                    self.display_message(file_messages[i], self.CONNECTED_USER_COLOR)
                self.semaphore.release()
                self.displayed_file_messages = file_messages.copy()

    def display_message(self, text, color):
        self.place_for_text_messages.tag_configure(color, background=color)
        self.place_for_text_messages.insert(tk.END, text + '\n', color)
        self.root.update()