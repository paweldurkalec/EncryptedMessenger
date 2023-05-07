import tkinter as tk
from tkinter import ttk, messagebox

from views.basic_view import BasicView
from views.add_new_key_view import AddNewKeyView
from views.choose_key_name_view import ChooseKeyNameView


class StartView(BasicView):

    PAD_Y = 150

    def __init__(self, root, images):
        super(StartView, self).__init__(root, images)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.display_widgets()

    def display_widgets(self):
        add_key_button = tk.Button(self.root, text='Dodaj nowy klucz', font = self.BUTTON_FONT, width=30, command=self.switch_to_add_key)
        add_key_button.pack(pady=self.PAD_Y)
        add_key_button = tk.Button(self.root, text='Użyj istniejącego klucza', font= self.BUTTON_FONT, width=30, command=self.switch_to_choose_old_key)
        add_key_button.pack(pady=self.PAD_Y/2)

    def on_closing(self):
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć program?"):
            self.root.destroy()

    def switch_to_add_key(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        AddNewKeyView(self.root, self.images)

    def switch_to_choose_old_key(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        ChooseKeyNameView(self.root, self.images)

