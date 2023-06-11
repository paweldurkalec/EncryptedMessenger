from lazy_import import lazy_module
import tkinter as tk
from tkinter import messagebox, filedialog
from threading import Semaphore
import os
from time import sleep
import shutil

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
        self.receiving_file = None
        self.canvas = None
        self.place_for_text_messages = None
        self.place_for_file_messages = None
        self.choosen_file = None
        self.file_label = None
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
            self.session.end()
            self.session.close_broadcast()
            self.root.destroy()

    def display_widgets(self):
        connected_user = tk.Label(self.root, bg=self.BACKGROUND_COLOR, font=self.BUTTON_FONT, text=f"Chat z użytkownikiem {self.session.connected_user.name}")
        connected_user.pack()

        self.root.update()
        label_width = connected_user.winfo_width()
        self.status = tk.Label(self.root, image=self.images['green'], bd=0)
        self.status.place(x=self.WIDTH/2 + label_width/2,y=0)
        self.place_for_text_messages = tk.Text(self.root)
        self.place_for_text_messages.place(x=20, y=50, width=300, height=400)
        self.place_for_file_messages = tk.Text(self.root)
        self.place_for_file_messages.place(x=400, y=50, width=300, height=400)
        scrollbar_text = tk.Scrollbar(self.root)
        scrollbar_text.config(command=self.place_for_text_messages.yview)
        scrollbar_text.place(x=320, y=50)
        self.place_for_text_messages.config(yscrollcommand=scrollbar_text.set)
        scrollbar_file = tk.Scrollbar(self.root)
        scrollbar_file.config(command=self.place_for_file_messages.yview)
        scrollbar_file.place(x=700, y=50)
        self.place_for_file_messages.config(yscrollcommand=scrollbar_file.set)
        self.text_input = tk.Entry(self.root, width=30)
        self.text_input.place(x=20, y=500, height=35)
        send_button = tk.Button(self.root, text='Wyslij', command=self.send_text_message, font=self.BUTTON_FONT)
        send_button.place(x=320, y=500)
        choose_file_button = tk.Button(self.root, font=self.BUTTON_FONT, text="Wybierz plik", command=self.choose_file,width=20)
        choose_file_button.place(x=400,y=500)
        send_file_button = tk.Button(self.root, text='Wyslij', command=self.send_file, font=self.BUTTON_FONT)
        send_file_button.place(x=650, y=500)
        tk.Button(self.root, text="Zamknij czat", command=self.switch_to_wait_for_chat).place(x=0,y=0)

    def choose_file(self):
        if not self.canvas:
            file_path = filedialog.askopenfilename()
            if file_path:
                if self.file_label:
                    self.file_label.destroy()
                    self.file_label.destroy()
                filename = os.path.basename(file_path)
                self.choosen_file = file_path
                self.file_label = tk.Label(self.root, text=filename, font=self.BUTTON_FONT,
                                               background=self.BACKGROUND_COLOR)
                self.file_label.place(x=400, y=550)

    def switch_to_wait_for_chat(self):
        self.thread.stop()
        if self.session.status == SessionStatus.ESTABLISHED:
            self.session.end()
        for widget in self.root.winfo_children():
            widget.destroy()
        wait_for_chat_module.WaitForChatView(self.root, self.private_key, self.name, self.images, self.public_keys, self.private_keys, self.session)

    def send_text_message(self):
        if not self.session.status == SessionStatus.ESTABLISHED:
            return
        text = self.text_input.get()
        self.text_input.delete(0, len(text))
        self.semaphore.acquire()
        self.display_text_message(text, self.MY_COLOR)
        self.semaphore.release()
        self.session.send_text_message(text)

    def send_file(self):
        if not self.session.status == SessionStatus.ESTABLISHED:
            return
        if self.file_label:
            if not os.path.isdir(self.FILES_DIR):
                os.mkdir(self.FILES_DIR)
            filename = os.path.basename(self.choosen_file)
            shutil.copyfile(self.choosen_file, os.path.join(self.FILES_DIR,filename))
            self.file_label.destroy()
            self.canvas = tk.Canvas(self.root, width=100, height=20)
            self.canvas.place(x=400,y=550)
            self.semaphore.acquire()
            self.display_file_message(filename, self.MY_COLOR)
            self.session.send_file(filename)
            self.displayed_file_messages = self.session.files
            self.semaphore.release()

    def finish_chat(self):
        self.status.configure(image=self.images["red"])
        self.thread.stop()

    def chat_with_connected_user(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.canvas:
                for file in reversed(self.session.files):
                    if file.type == 'SENT':
                        if file.percentage == 100:
                            self.canvas.destroy()
                            self.canvas = None
                        else:
                            self.canvas.delete("all")
                            self.canvas.create_rectangle(0, 0, file.percentage, 30, fill="blue")
            if self.receiving_file and self.receiving_file.percentage == 100:
                self.semaphore.acquire()
                self.display_file_message(self.receiving_file.file_name, self.CONNECTED_USER_COLOR)
                self.semaphore.release()
                self.receiving_file = None
            if self.session.status == SessionStatus.UNESTABLISHED:
                self.root.after(0, lambda: self.finish_chat())
                return
            text_messages = self.session.text_messages
            file_messages = self.session.files
            if self.displayed_text_messages != text_messages:
                self.semaphore.acquire()
                for i in range(len(self.displayed_text_messages), len(text_messages)):
                    self.display_text_message(text_messages[i], self.CONNECTED_USER_COLOR)
                self.semaphore.release()
                self.displayed_text_messages = text_messages.copy()
            if self.displayed_file_messages != file_messages:
                self.semaphore.acquire()
                for i in range(len(self.displayed_file_messages), len(file_messages)):
                    if file_messages[i].type == 'RECEIVED':
                        if file_messages[i].percentage == 100:
                            self.display_file_message(file_messages[i].file_name, self.CONNECTED_USER_COLOR)
                        else:
                            self.receiving_file = file_messages[i]
                self.semaphore.release()
                self.displayed_file_messages = file_messages.copy()
            sleep(0.5)

    def display_text_message(self, text, color):
        self.place_for_text_messages.tag_configure(color, background=color)
        self.place_for_text_messages.insert(tk.END, text + '\n', color)
        self.root.update()

    def display_file_message(self, text, color):
        self.place_for_file_messages.tag_configure(color, background=color)
        self.place_for_file_messages.insert(tk.END, text + '\n', color)
        self.root.update()