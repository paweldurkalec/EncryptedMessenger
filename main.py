from Crypto.PublicKey import RSA
from PIL import ImageTk, Image
import tkinter as tk


from views.wait_for_chat_view import WaitForChatView

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Messenger")
    root.resizable(False, False)  # set fixed window size
    root.geometry(f"{800}x{600}")
    root.configure(bg='white')
    back_arrow = Image.open("images/back_arrow.png")
    back_arrow = back_arrow.resize((50, 50), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(back_arrow)
    images = {"back_arrow": photo}

    with open('test_public_key.txt', 'rb') as f:
        public_key = RSA.importKey(f.read())

    with open('test_private_key.txt', 'rb') as f:
        private_key = RSA.importKey(f.read())
    WaitForChatView(root, private_key, public_key,'PAWEL-PC2', images)
    root.mainloop()
