import Tkinter as tk
import Image, ImageTk

import config

class Label(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self.config(bg=config.BGCOLOR, fg=config.FGCOLOR, font=(config.FONT, config.NORMAL))


class Button(tk.Frame):
    def __init__(self, *args, **kwargs):
        self.image = self.load_image(name=kwargs.pop('button_img', 'button_center'))
        self.image_left = self.load_image(name=kwargs.pop('button_left', 'button_left'))
        self.image_right = self.load_image(name=kwargs.pop('button_right', 'button_right'))
        self.text = kwargs.pop('text', '')
        
        tk.Frame.__init__(self, *args, **kwargs)
        self.config(pady=20, bg=config.BGCOLOR)

        self.left = tk.Label(self, image=self.image_left)
        self.left.config(bg=config.BGCOLOR, bd=0, padx=0, pady=0)
        self.left.pack(side=tk.LEFT)

        self.center = tk.Label(self, image=self.image, text=self.text)
        self.center.config(bg=config.BGCOLOR, fg=config.FGCOLOR, font=config.BOLD, bd=0, padx=0, pady=0)
        self.center.config(compound=tk.CENTER)
        self.center.pack(side=tk.LEFT)

        self.right = tk.Label(self, image=self.image_right)
        self.right.config(bg=config.BGCOLOR, bd=0, padx=0, pady=0)
        self.right.pack(side=tk.LEFT)

    # Propagate bindings to button's images
    def bind(self, *args, **kwargs):
        tk.Frame.bind(self, *args, **kwargs)
        for child in self.winfo_children():
            child.bind(*args, **kwargs)

    def update_left(self, imagename):
        self.image_left = self.load_image(name=imagename)
        self.left.config(image=self.image_left)

    def update_right(self, imagename):
        self.image_right= self.load_image(name=imagename)
        self.right.config(image=self.image_right)

    def update_text(self, newtext):
        self.center.config(text=newtext)

    def load_image(self, name):
        filename = 'assets/' + name + '.png'
        image = None # Is there any need to keep a reference to prevent GC?
        if config.FACTOR == 1.0:
            image = ImageTk.PhotoImage(file=filename) 
        else:
            original = Image.open(filename)
            width = int(original.size[0]*config.FACTOR)
            height = int(original.size[1]*config.FACTOR)
            resized = original.resize((width, height), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(resized)
        return image

