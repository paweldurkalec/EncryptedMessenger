from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from views.chat_view import ChatView


class WaitForChatView(BasicView):

    def __init__(self, root, private_key, public_key, name, images, session=None):
        super(WaitForChatView, self).__init__(root, images)
        if session:
            self.session = session
        else:
            self.session = self.initialize_session(private_key, name)
        self.public_key = public_key
        self.private_key = private_key
        self.listbox = None
        self.place_for_users = None
        self.online_users = session.user_list
        self.display_widgets()


    def display_widgets(self):
        label = tk.Label(self.root, image=self.images['back_arrow'], bd=0)
        label.place(x=0, y=0)
        label = tk.Label(self.root, font=self.MAX_FONT, text="Lista dostępnych użytkowników", bg=self.BACKGROUND_COLOR)
        label.pack(pady=self.PAD_Y)
        self.place_for_users = tk.Frame(self.root, width=300, height=400)
        self.place_for_users.pack_propagate(0)
        self.place_for_users.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.display_online_users()
        self.thread = StoppableThread(self.check_users_actions)
        self.thread.thread.start()

    def initialize_session(self, private_key, name):
        session = Session(name, private_key)
        session.open_broadcast()
        return session

    def answer_to_invitation(self):
        result = messagebox.askquestion("Zaproszenie do chatu", f"Czy chcesz przystąpić do chatu z {self.session.connected_user.name}", icon="question", default="yes",
                                        parent=self.root, yesno="tak/nie")
        if result == 'yes':
            self.session.accept()
            self.switch_to_chat()


    def check_users_actions(self):
        if self.session.status == SessionStatus.WAITING_FOR_ACCEPTANCE:
            self.answer_to_invitation()
        online_users = self.session.user_list
        if online_users != self.online_users:
            self.online_users = online_users
            self.refresh_place_for_users()
            self.display_online_users()
        sleep(1)

    def display_online_users(self):
        self.listbox = tk.Listbox(self.place_for_users, justify="center", font=self.BUTTON_FONT)
        for item in ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]:
            self.listbox.insert(tk.END, item)

        scrollbar = ttk.Scrollbar(self.place_for_users, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind("<Double-Button-1>", self.handle_double_click)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_place_for_users(self):
        for widget in self.place_for_users.winfo_children():
            widget.destroy()

    def handle_double_click(self, event):
        # get the selected item from the listbox
        selection = self.listbox.curselection()
        if len(selection) == 1:
            index = selection[0]
            item = self.listbox.get(index)
            print(f"You double clicked {item}")

    def switch_to_chat(self):
        self.thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        ChatView(self.root, self.private_key, self.public_key, self.name, self.images)
