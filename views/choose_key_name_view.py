from lazy_import import lazy_module
import paramiko
from time import sleep
import tkinter as tk
from tkinter import ttk, messagebox
import os

from session import Session, SessionStatus
from stoppable_thread import StoppableThread
from views.basic_view import BasicView
from views.chat_view import ChatView
from views.choose_encription_and_key import ChooseEncriptionAndKey
from views.add_new_key_view import AddNewKeyView
from views.wait_for_chat_view import WaitForChatView

start_view_module = lazy_module("views.start_view")

class ChooseKeyNameView(BasicView):

    def __init__(self, root, images):
        super(ChooseKeyNameView, self).__init__(root, images)
        self.listbox = None
        self.place_for_keys = None
        self.private_keys = [f for f in os.listdir(self.PRIVATE_KEY_DIR) if os.path.isfile(os.path.join(self.PRIVATE_KEY_DIR, f))]
        if not self.private_keys:
            messagebox.showerror("Brak kluczy", "Nie dodałeś żadnych prywatnych kluczy. Aby kontynuować dodaj odpowiedni klucz")
            AddNewKeyView(self.root, images)
            return
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
        try:
            private_key = paramiko.RSAKey(filename=path_to_selected_key, password=password)
            private_key.can_sign()
        except paramiko.ssh_exception.SSHException as e:
                messagebox.showerror("Złe hasło",
                                     "Podano złe hasło.")
                return
        if not(name:=self.entry_name.get()):
            messagebox.showerror("Brak nazwy",
                                 "Podaj nazwę użytkownika, aby kontynuować.")
            return
        for widget in self.root.winfo_children():
            widget.destroy()
        WaitForChatView(self.root, path_to_selected_key, name, self.images)
        pass

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