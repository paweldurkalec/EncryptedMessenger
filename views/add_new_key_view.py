import os.path

from lazy_import import lazy_module
import paramiko
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from views.basic_view import BasicView

start_view_module = lazy_module("views.start_view")


class AddNewKeyView(BasicView):

    PAD_Y = 150
    def __init__(self, root, images):
        super(AddNewKeyView, self).__init__(root, images)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.entry_name = None
        self.entry_password = None
        self.key_type_var = tk.StringVar() #set it to private
        self.key_type_var.set("private")
        self.key_path = None
        self.display_widgets()
        self.key_path_label = None

    def display_widgets(self):
        label = tk.Label(self.root, image=self.images['back_arrow'], bd=0)
        label.place(x=0, y=0)
        label.bind("<Button-1>", self.switch_to_start_view)
        label = tk.Label(self.root, font = self.BUTTON_FONT, text="Wpisz nazwę klucza", background=self.BACKGROUND_COLOR)
        label.place(x=100,y=150)
        self.entry_name = tk.Entry(self.root, font=self.BUTTON_FONT,width=25)
        self.entry_name.place(x=50, y=200)
        label = tk.Label(self.root, font=self.BUTTON_FONT, text="Wpisz hasło", background=self.BACKGROUND_COLOR)
        label.place(x=450, y=150)
        self.entry_password = tk.Entry(self.root, font=self.BUTTON_FONT,width=25)
        self.entry_password.place(x=400, y=200)
        private_type = tk.Radiobutton(self.root, background=self.BACKGROUND_COLOR,font=self.BUTTON_FONT, variable=self.key_type_var, text="Klucz prywatny", value="private")
        private_type.place(x=50, y=300)
        public_type = tk.Radiobutton(self.root, font=self.BUTTON_FONT, variable=self.key_type_var, background=self.BACKGROUND_COLOR,text="Klucz publiczny",
                              value="public")
        public_type.place(x=50, y=350)
        button_key = tk.Button(self.root, font=self.BUTTON_FONT, text="Wybierz klucz", command=self.open_file, width=20)
        button_key.place(x=400, y=300)
        add_key_button = tk.Button(self.root, font=self.BUTTON_FONT, text="Dodaj klucz", command=self.add_key, width=20)
        add_key_button.place(x=400, y=400)

    def switch_to_start_view(self, event=None):
        for widget in self.root.winfo_children():
            widget.destroy()
        start_view_module.StartView(self.root, self.images)

    def add_key(self):
        if not self.entry_name.get():
            messagebox.showerror("Brak nazwy klucza",
                                 "Nie wpisano nazwy klucza.")
            return
        if not self.key_path:
            messagebox.showerror("Brak klucza",
                                 "Nie wybrano klucza.")
            return
        if self.key_type_var.get()=="public":
            if self.key_path[-3:] != "pub":
                messagebox.showerror("Zły typ",
                                     "Wybrano zły typ klucza.")
                return
            else:
                filename = self.entry_name.get()
                path_to_key = self.key_path
                destination = f"{self.WORKING_DIR}/ssh_public/{filename}.pub"
                if os.path.isfile(destination):
                    messagebox.showerror("Nieunikatowa nazwa",
                                         "Taka nazwa klucza już istanieje. Wybierz nową.")
                    return
                shutil.copy(path_to_key,destination)
        else:
            if self.key_path[-3:] == "pub":
                messagebox.showerror("Zły typ",
                                     "Wybrano zły typ klucza.")
                return
            if not self.entry_password.get():
                messagebox.showerror("Brak hasła",
                                     "Nie wybrano hasła.")
                return
            filename = self.entry_name.get()
            path_to_key = self.key_path
            destination = f"{self.WORKING_DIR}/ssh_private/{filename}"
            try:
                private_key = paramiko.RSAKey(filename=self.key_path, password=self.entry_password.get())
                private_key.can_sign()
            except paramiko.ssh_exception.SSHException as e:
                if e.args[0] == "OpenSSH private key file checkints do not match":
                    messagebox.showerror("Złe hasło",
                                         "Podano złe hasło.")
                    return
                else:
                    messagebox.showerror("Zły plik",
                                         "Podano zły plik.")
                    return
            if os.path.isfile(destination):
                messagebox.showerror("Nieunikatowa nazwa",
                                     "Taka nazwa klucza już istanieje. Wybierz nową.")
                return
            shutil.copy(path_to_key, destination)
        self.switch_to_start_view()

    def allowed_extensions(self):
        ret = ""
        for extension in self.ALLOWED_EXTENSIONS:
            ret += f"{extension} "
        return ret[:-1]

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            if self.key_path_label:
                self.key_path_label.destroy()
            filename = os.path.basename(file_path)
            self.key_path_label = tk.Label(self.root, text=filename,font=self.BUTTON_FONT, background=self.BACKGROUND_COLOR)
            self.key_path_label.place(x=400,y=350)
            self.key_path = file_path


    def on_closing(self):
        if messagebox.askokcancel("Wyjście", "Czy na pewno chcesz zamknąć program?"):
            self.root.destroy()

