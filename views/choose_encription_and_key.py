from lazy_import import lazy_module
from tkinter import messagebox
import tkinter as tk

from session import SessionStatus
from views.basic_view import BasicView
from views.chat_view import ChatView
from stoppable_thread import StoppableThread

wait_for_chat_module = lazy_module('views.wait_for_chat_view')


class ChooseEncriptionAndKey(BasicView):

    def __init__(self, root, private_key, name, images, session, user_name, public_keys, private_keys, user_address):
        super(ChooseEncriptionAndKey, self).__init__(root, images, public_keys, private_keys)
        self.user_adress = user_address
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.checking_thread = None
        if not user_address:
            self.checking_thread = StoppableThread(self.wait_for_other_user)
        self.session = session
        self.user_name = user_name
        self.private_key = private_key
        self.name = name
        self.listbox = None
        self.place_for_keys = None
        self.display_widgets()
        self.encryption_type_var = tk.StringVar()
        self.encryption_type_var.set("ECB")
        self.user_adress = None
        if self.user_adress:
            self.waiting_thread = StoppableThread(self.wait_for_other_user)

    def check_for_timeout(self, stop_event):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.UNESTABLISHED:
                self.root.after(0, lambda: self.switch_to_wait_for_chat())

    def on_closing(self):
        if self.user_adress and not self.waiting_thread:
            if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć program?"):
                self.root.destroy()
                self.session.close_broadcast()

    def display_widgets(self):
        label = tk.Label(self.root, font=self.BUTTON_FONT, text=f"Wybierz klucz publiczny użytkownika{self.user_name}", bg=self.BACKGROUND_COLOR)
        label.pack(pady=self.PAD_Y)
        self.place_for_keys = tk.Frame(self.root, width=300, height=400)
        self.place_for_keys.pack_propagate(0)
        self.place_for_keys.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Wpisz nazwe użytkownika",
                         background=self.BACKGROUND_COLOR)
        label.place(x=400, y=170)
        private_type = tk.Radiobutton(self.root, background=self.BACKGROUND_COLOR, font=self.BUTTON_FONT,
                                      variable=self.key_type_var, text="ECB", value="private")
        private_type.place(x=50, y=300)
        public_type = tk.Radiobutton(self.root, font=self.BUTTON_FONT, variable=self.key_type_var,
                                     background=self.BACKGROUND_COLOR, text="CBC",
                                     value="public")
        public_type.place(x=50, y=350)
        button_key = tk.Button(self.root, font=self.BUTTON_FONT, text="Połącz",
                               command=self.start_wait_for_other_user, width=20)
        button_key.place(x=420, y=300)
        self.display_keys()

    def display_keys(self):
        self.listbox = tk.Listbox(self.place_for_keys, justify="center", font=self.BUTTON_FONT)
        for key in self.public_keys:
            self.listbox.insert(tk.END, key)
        scrollbar = tk.Scrollbar(self.place_for_keys, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def switch_to_chat(self):
        if self.waiting_thread:
            self.waiting_thread.stop()
        if self.checking_thread:
            self.checking_thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        ChatView(self.root, self.private_key, self.public_key, self.name, self.images, self.session, self.public_keys, self.private_keys)

    def switch_to_wait_for_chat(self):
        if self.waiting_thread:
            self.waiting_thread.stop()
        if self.checking_thread:
            self.checking_thread.stop()
        for widget in self.root.winfo_children():
            widget.destroy()
        wait_for_chat_module.WaitForChatView(self.root, self.private_key, self.name, self.images, self.public_keys, self.private_keys, self.session)

    def wait_for_other_user(self, stop_event, **kwargs):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.ESTABLISHED:
                self.root.after(0, lambda: self.switch_to_chat())
            if self.session.status == SessionStatus.UNESTABLISHED:
                self.root.after(0, lambda: self.switch_to_wait_for_chat())

    def display_wait(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        label = tk.Label(self.root, font=self.MAX_FONT, text="Trwa oczekiwanie na drugą osobę", background=self.BACKGROUND_COLOR)
        label.place(anchor=tk.CENTER)

    def start_waiting_for_other_user(self):
        if self.user_adrress:
            self.session.send_init(self.user_name,self.user_adress , public_key=self.public_key)
            self.waiting_thread.start()
            self.display_wait()
        else:
            self.session.accept(self.public_key)
            self.switch_to_chat()