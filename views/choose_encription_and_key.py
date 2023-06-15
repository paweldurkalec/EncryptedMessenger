from lazy_import import lazy_module
from tkinter import messagebox
import tkinter as tk
from Crypto.PublicKey import RSA
import os

from session import SessionStatus
from views.basic_view import BasicView
from views.chat_view import ChatView
from stoppable_thread import StoppableThread

wait_for_chat_module = lazy_module('views.wait_for_chat_view')


class ChooseEncriptionAndKey(BasicView):

    def __init__(self, root, private_key, name, images, session, user_name, public_keys, private_keys, user_address):
        super(ChooseEncriptionAndKey, self).__init__(root, images, public_keys, private_keys)
        self.send_invitation = False
        self.user_address = user_address
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.checking_thread = None
        self.session = session
        if not self.user_address:
            self.checking_thread = StoppableThread(self.check_for_timeout)
            self.checking_thread.thread.start()
        self.user_name = user_name
        self.private_key = private_key
        self.name = name
        self.listbox = None
        self.place_for_keys = None
        self.encryption_type_var = tk.StringVar()
        self.encryption_type_var.set("ECB")
        self.display_widgets()
        self.waiting_thread = None
        if self.user_address:
            self.waiting_thread = StoppableThread(self.wait_for_other_user)
            self.waiting_thread.thread.start()

    def check_for_timeout(self, stop_event):
        while not stop_event.is_set():
            if self.session.status == SessionStatus.UNESTABLISHED:
                self.root.after(0, lambda: self.switch_to_wait_for_chat())

    def get_selected_key(self):
        selection = self.listbox.curselection()
        if len(selection) == 1:
            index = selection[0]
            return self.listbox.get(index)
        return

    def on_closing(self):
        if self.user_adress and not self.waiting_thread:
            if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć program?"):
                self.root.destroy()
                self.session.close_broadcast()

    def display_widgets(self):
        if self.user_address:
            label = tk.Label(self.root, image=self.images['back_arrow'], bd=0)
            label.place(x=0, y=0)
            label.bind("<Button-1>", self.switch_to_wait_for_chat)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text=f"Wybierz klucz publiczny użytkownika {self.user_name}", bg=self.BACKGROUND_COLOR)
        label.pack(pady=self.PAD_Y)
        self.place_for_keys = tk.Frame(self.root, width=300, height=200)
        self.place_for_keys.pack_propagate(0)
        self.place_for_keys.pack(pady=self.PAD_Y)
        if self.user_address:
            ecb_button = tk.Radiobutton(self.root, background=self.BACKGROUND_COLOR, font=self.BUTTON_FONT,
                                          variable=self.encryption_type_var, text="ECB", value="ECB")
            ecb_button.pack(pady=self.PAD_Y/3)
            cbc_button = tk.Radiobutton(self.root, font=self.BUTTON_FONT, variable=self.encryption_type_var,
                                         background=self.BACKGROUND_COLOR, text="CBC",
                                         value="CBC")
            cbc_button.pack(pady=self.PAD_Y/3)
        button_key = tk.Button(self.root, font=self.BUTTON_FONT, text="Połącz",
                               command=self.start_wait_for_other_user, width=20)
        button_key.pack(pady=self.PAD_Y/3)
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
        ChatView(self.root, self.private_key, self.name, self.images, self.session, self.public_keys, self.private_keys)

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
                return
            elif self.session.status == SessionStatus.UNESTABLISHED and self.send_invitation==True:
                self.root.after(0, lambda: self.switch_to_wait_for_chat())
                return
            elif self.session.status == SessionStatus.WAITING_FOR_ACCEPTANCE:
                self.session.decline()
                return

    def display_wait(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Trwa oczekiwanie na drugą osobę", background=self.BACKGROUND_COLOR)
        label.pack(pady=self.PAD_Y)

    def start_wait_for_other_user(self):
        if self.user_address:
            public_key = self.get_public_key()
            block_cipher = self.encryption_type_var.get()
            self.session.send_init(self.user_name,self.user_address, public_key=public_key, block_cipher=block_cipher)
            self.send_invitation = True
            self.display_wait()
        else:
            public_key = self.get_public_key()
            self.session.accept(public_key=public_key)
            self.switch_to_chat()

    def get_public_key(self):
        selected_key = self.get_selected_key()
        if not selected_key:
            messagebox.showerror("Wybierz klucz",
                                 "Aby kontynuować wybierz klucz publiczny")
            return
        path_to_selected_key = os.path.join(self.PUBLIC_KEY_DIR, selected_key)
        with open(path_to_selected_key, 'rb') as f:
            return RSA.importKey(f.read())