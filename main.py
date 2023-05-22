from Crypto.PublicKey import RSA
from PIL import ImageTk, Image
import tkinter as tk

from views.wait_for_chat_view import WaitForChatView
from views.start_view import StartView




def load_images():
    back_arrow = Image.open("images/back_arrow.png")
    back_arrow = back_arrow.resize((50, 50), Image.ANTIALIAS)
    back_arrow = ImageTk.PhotoImage(back_arrow)
    red = Image.open("images/red.png")
    red = red.resize((10, 10), Image.ANTIALIAS)
    red = ImageTk.PhotoImage(red)
    green = Image.open("images/green.png")
    green = green.resize((10, 10), Image.ANTIALIAS)
    green = ImageTk.PhotoImage(green)
    images = {"back_arrow": back_arrow, "red":red,"green":green}
    return images

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Messenger")
    root.resizable(False, False)  # set fixed window size
    root.geometry(f"{800}x{600}")
    root.configure(bg='white')
    images = load_images()

    with open('test_public_key.txt', 'rb') as f:
        public_key = RSA.importKey(f.read())

    with open('test_private_key.txt', 'rb') as f:
        private_key = RSA.importKey(f.read())
    StartView(root, images)
    #WaitForChatView(root, private_key, public_key,'PAWEL-PC2', images) #uncomment for testing
    root.mainloop()

