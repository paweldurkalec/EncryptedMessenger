import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Listbox with Scrollbar and Binded Function")

my_listbox = tk.Listbox(root)
for item in ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]:
    my_listbox.insert(tk.END, item)

my_scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=my_listbox.yview)
my_listbox.configure(yscrollcommand=my_scrollbar.set)

def on_select(event):
    selected_item = my_listbox.get(my_listbox.curselection())
    print(selected_item)

my_listbox.bind("<<ListboxSelect>>", on_select)

my_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()