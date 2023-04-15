from time import sleep
import tkinter as tk
from tkinter import ttk

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView


class WaitForChatView(BasicView):

    def __init__(self, root, private_key, name, images, session=None):
        super(WaitForChatView, self).__init__(root, images)
        if session:
            self.session = session
        else:
            self.session = self.initialize_session(private_key, name)
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

    def check_users_actions(self):
        if self.session.status == SessionStatus.WAITING_FOR_ACCEPTANCE:
            pass
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












#while len(session.user_list) < 1:
#    time.sleep(1)
#
#time.sleep(5)
#session.send_init(session.user_list[0].name, session.user_list[0].address, public_key=public_key)
#
#while session.status != SessionStatus.ESTABLISHED:
#    time.sleep(1)
#
#while session.status == SessionStatus.ESTABLISHED:
#    print("Podaj tresc wiadomosci do wyslania: ")
#    msg = input()
#    session.send_text_message(msg)