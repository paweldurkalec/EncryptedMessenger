from lazy_import import lazy_module
import paramiko
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
import os
import hashlib
from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from views.chat_view import ChatView
from views.choose_encription_and_key import ChooseEncriptionAndKey
from views.add_new_key_view import AddNewKeyView
from views.wait_for_chat_view import WaitForChatView
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

start_view_module = lazy_module("views.start_view")

class ChooseKeyNameView(BasicView):

    def __init__(self, root, images, public_keys, private_keys):
        super(ChooseKeyNameView, self).__init__(root, images, public_keys, private_keys)
        self.listbox = None
        self.place_for_keys = None
        self.entry_name = None
        self.entry_password = None
        self.display_widgets()

    def display_widgets(self):
        label = tk.Label(self.root, image=self.images['back_arrow'], bd=0)
        label.place(x=0, y=0)
        label.bind("<Button-1>", self.switch_to_start_view)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Lista kluczy prywatnych", bg=self.BACKGROUND_COLOR)
        label.place(x=100,y=50)
        self.place_for_keys = tk.Frame(self.root, width=300, height=400)
        self.place_for_keys.pack_propagate(0)
        self.place_for_keys.place(x=50,y=100)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Wpisz hasło", background=self.BACKGROUND_COLOR)
        label.place(x=400, y=70)
        self.entry_password = tk.Entry(self.root, font=self.BUTTON_FONT, width=25)
        self.entry_password.place(x=400, y=100)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Wpisz nazwe użytkownika", background=self.BACKGROUND_COLOR)
        label.place(x=400, y=170)
        self.entry_name = tk.Entry(self.root, font=self.BUTTON_FONT, width=25)
        self.entry_name.place(x=400, y=200)
        button_key = tk.Button(self.root, font=self.BUTTON_FONT, text="Połącz", command=self.switch_to_waiting_for_chat_view, width=20)
        button_key.place(x=420, y=300)
        self.display_keys()

    def get_selected_key(self):
        selection = self.listbox.curselection()
        if len(selection) == 1:
            index = selection[0]
            return self.listbox.get(index)
        return

    def decrypt_key(self,password, path_to_key):
        key_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), self.salt, iterations=100000)
        key_hash = key_hash[:32]
        block_size = 16
        decrypted_key = ''
        with open(path_to_key, 'rb') as infile:
            iv = infile.read(block_size)
            cipher = AES.new(key_hash, AES.MODE_CBC, iv)
            while True:
                block = infile.read(block_size)
                if len(block) == 0:
                    break
                decrypted_key+=cipher.decrypt(block).decode("utf-8")
        return RSA.import_key(decrypted_key)


    def switch_to_waiting_for_chat_view(self):
        selected_key = self.get_selected_key()
        if not selected_key:
            messagebox.showerror("Wybierz klucz",
                                 "Aby kontynuować, wybierz klucz prywatny")
            return
        path_to_selected_key = os.path.join(self.PRIVATE_KEY_DIR,selected_key)
        if not(password:=self.entry_password.get()):
            messagebox.showerror("Brak hasła",
                                 "Podaj hasło do klucza publicznego.")
            return
        decrypted_key = self.decrypt_key(password, path_to_selected_key)

        if not(name:=self.entry_name.get()):
            messagebox.showerror("Brak nazwy",
                                 "Podaj nazwę użytkownika, aby kontynuować.")
            return
        for widget in self.root.winfo_children():
            widget.destroy()
        WaitForChatView(self.root, decrypted_key, name, self.images, self.public_keys, self.private_keys)

    def display_keys(self):
        self.listbox = tk.Listbox(self.place_for_keys, justify="center", font=self.BUTTON_FONT)
        for key in self.private_keys:
            self.listbox.insert(tk.END, key)
        scrollbar = ttk.Scrollbar(self.place_for_keys, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def switch_to_start_view(self, event=None):
        for widget in self.root.winfo_children():
            widget.destroy()
        start_view_module.StartView(self.root, self.images)