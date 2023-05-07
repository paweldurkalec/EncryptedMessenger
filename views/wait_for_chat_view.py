from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from views.chat_view import ChatView
from views.choose_encription_and_key import ChooseEncriptionAndKey


class WaitForChatView(BasicView):

    def __init__(self, root, private_key, name, images, session=None):
        super(WaitForChatView, self).__init__(root, images)
        if session:
            self.session = session
        else:
            self.session = self.initialize_session(private_key, name)
        self.name = name
        self.private_key = private_key
        self.listbox = None
        self.place_for_users = None
        self.online_users = self.session.user_list.copy()
        self.display_widgets()
        self.thread = StoppableThread(self.check_users_actions)
        self.thread.thread.start()

    def display_widgets(self):
        label = tk.Label(self.root, image=self.images['back_arrow'], bd=0)
        label.place(x=0, y=0)
        label = tk.Label(self.root, font=self.MAX_FONT, text="Lista dostępnych użytkowników", bg=self.BACKGROUND_COLOR)
        label.pack(pady=self.PAD_Y)
        self.place_for_users = tk.Frame(self.root, width=300, height=400)
        self.place_for_users.pack_propagate(0)
        self.place_for_users.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.display_online_users()

    def initialize_session(self, private_key, name):
        session = Session(name, private_key)
        session.open_broadcast()
        return session

    def answer_to_invitation(self):
        result = messagebox.askquestion("Zaproszenie do chatu", f"Czy chcesz przystąpić do chatu z {self.session.connected_user.name}", icon="question", default="yes",
                                        parent=self.root)
        if result == 'yes':
            self.session.accept(self.public_key)
            self.switch_to_chat()

    def check_users_actions(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.WAITING_FOR_ACCEPTANCE:
                self.answer_to_invitation()
            online_users = self.session.user_list.copy()
            if online_users != self.online_users:
                self.online_users = online_users
                self.refresh_place_for_users()
                self.display_online_users()
            sleep(1)

    def display_online_users(self):
        self.listbox = tk.Listbox(self.place_for_users, justify="center", font=self.BUTTON_FONT)
        for user in self.online_users:
            self.listbox.insert(tk.END, user.name)

        scrollbar = ttk.Scrollbar(self.place_for_users, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind("<Double-Button-1>", self.handle_double_click)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_place_for_users(self):
        for widget in self.place_for_users.winfo_children():
            widget.destroy()

    def handle_double_click(self, event):
        selection = self.listbox.curselection()
        if len(selection) == 1:
            index = selection[0]
            user_name = self.listbox.get(index)
            for user in self.session.user_list:
                if user.name == user_name:
                    self.session.send_init(user.name, user.address, public_key=self.public_key)
                    self.switch_to_choose_encription()
                    break

    def switch_to_chat(self):
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        ChatView(self.root, self.private_key, self.public_key, self.name, self.images, self.session)

    def switch_to_choose_encription(self):
        self.thread.stop()
        print('destroying')
        for widget in self.root.winfo_children():
            widget.destroy()
        ChooseEncriptionAndKey(self.root, self.private_key, self.public_key, self.name, self.images, self.session)