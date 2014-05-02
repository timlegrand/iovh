# coding=utf-8

import dateutil.parser as du
import Tkinter as tk
import Image, ImageTk
import os, sys
import webbrowser

import config
from gui_utils import *

class GUI(tk.Tk):
    ''' iOVH interface only.
        Not app. '''
    
    def __init__(self, *args, **kwargs):
        print 'Launching GUI...'
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('iOVH')
        self.config(bg=config.BGCOLOR)
        self.geometry("%dx%d+200+100" % (config.WIDTH, config.HEIGHT))
        self.resizable(width=False, height=False)
        self.categories = ['mails', 'settings', 'power']
        ### Create the login frame
        self.login = ContentFrame.forCategory(self, 'login')
        self.login.pack_forget()
        
    def build_menu(self, categories):
        self.categories = categories + self.categories # Prepend extra categories to default
        self.menu = MenuFrame(self)
        self.separator = tk.Frame(self)
        self.separator.config(bg=config.BGCOLOR, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    def build_content_frames(self):
        self.content_frames = {}
        for cat in self.categories:
            cf = ContentFrame.forCategory(self, cat)
            self.content_frames[cat] = cf
            cf.pack_forget()
        if not self.content_frames:
            raise GuiFrameListEmptyException
        
        self.current_frame = self.content_frames.values()[0]
        self.content_frames.values()[0].show()
        print 'GUI ready.'

    def wait_for_click(self):
        self.wait_variable(self.login.step)

    def run(self):
        self.mainloop()


class MenuFrame(tk.Frame):
    ''' Menu frame for iOVH interface.
        You may also need a content frame in your root GUI. '''
    
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.config(bg=config.BGCOLOR)
        self.pack(side=tk.TOP, fill=tk.X)
        self.current_category = tk.StringVar()
        self.current_category.set('domains')
        self.current_category.trace('w', self.update)

        ### Create menu widgets
        self.icons = []
        for cat in self.master.categories:
            original = ImageTk.PhotoImage(file='assets/icon_' + cat + '.png')
            self.icons.append(original) # Keep a reference, prevent GC
            icon_label = tk.Label(self)
            icon_label.config(image=self.icons[-1], bg=config.BGCOLOR, padx=0, pady=0, bd=0)
            icon_label.pack(side=tk.LEFT, expand=True)
            icon_label.bind("<Button-1>", lambda event, arg=cat: self.current_category.set(arg))

    def update(self, *args):
        self.master.content_frames[self.current_category.get()].show() 
        self.master.current_frame = self.master.content_frames[self.current_category.get()]
        self.master.update_idletasks() # Don't wait for a mouse move to update content frame
 

class ContentFrame(tk.Frame):
    ''' Factory for buiding main content frames.
        You may also need a menu frame in your root GUI. '''
    
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.entry_count = 0
        self.config(bg=config.BGCOLOR)
        self.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    
    @classmethod
    def forCategory(cls, master, category):
        cf = None
        if category is 'bills':
            cf = BillsContentFrame(master)
        elif category is 'domains':
            cf = DomainsContentFrame(master)
        elif category is 'me':
            cf = MeContentFrame(master)
        elif category is 'stats':
            cf = HostingsWebContentFrame(master)
        elif category is 'power':
            cf = PowerContentFrame(master)
        elif category is 'login':
            cf = LoginContentFrame(master)
        else:
            cf = ContentFrame(master)
        return cf

    def add_entry(self, entry):
        raise NotImplementedError, "No implementation of add_entry for %s" % self.__class__

    def add_entries(self, entries):
        for e in entries.items():
            self.add_entry(e)

    def show(self):
        if self.master.current_frame:
            self.master.current_frame.pack_forget() 
        self.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.master.current_frame = self


class BillsContentFrame(ContentFrame):
    def add_entry(self, bill):
        self.entry_count += 1
        
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=100)
        entry.pack(fill=tk.X, expand=False)
        entry.pack_propagate(False) # Fixes frame size regardless of its (packed) contents
        date = du.parse(bill.date.encode('ascii', 'ignore')).strftime('%Y/%m/%d')
        date_label = Label(entry, text=date)
        date_label.config(anchor=tk.NW)
        date_label.pack(side=tk.LEFT)
        id_label = Label(entry, text="Facture %s" % bill.billId)
        id_label.config(font=('Arial', 12))
        id_label.pack(side=tk.LEFT)
        price_label = Label(entry, text=bill.priceWithTax['text'])
        price_label.config(padx=15, font=config.BOLD)
        price_label.pack(side=tk.RIGHT)
        
        separator = tk.Frame(self)
        separator.config(bg=config.BGCOLOR, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=25, pady=5)

    def on_click(self):
        self.expand()

    def expand(self):
        pass
        

class DomainsContentFrame(ContentFrame):
    def add_entry(self, domain):
        self.entry_count += 1
        
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=100)
        entry.grid()
        
        domain_label = Label(entry, text=domain.domain)
        domain_label.config(bg=config.BGCOLOR, padx=10, font=config.BOLD)
        domain_label.grid(sticky=tk.W, row=0, column=0)
        date = du.parse(domain.lastUpdate.encode('ascii', 'ignore')).strftime('%Y/%m/%d')
        lastUpdate_label = Label(entry, text='Last update: %s' % date)
        lastUpdate_label.grid(sticky=tk.W, row=1, column=0)
        status_label = Label(entry, text='Status: '+domain.transferLockStatus)
        status_label.grid(sticky=tk.W, row=2, column=0)
            

class HostingsWebContentFrame(ContentFrame):
    def add_entry(self, hosting):
        self.entry_count += 1
        
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=300)
        entry.grid()
        
        i = 0
        for k, v in hosting.__dict__.items():
            if v is None or isinstance(v, dict):
                continue
            text = k + ': ' + v
            l = Label(entry, text=text)
            if k == 'serviceName':
                l.config(padx=10, font=config.BOLD)
            l.grid(sticky=tk.W, row=i, column=0)
            i += 1
            

class MeContentFrame(ContentFrame):
    def add_entry(self, me):
        self.entry_count += 1
        
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=100)
        entry.grid()
        name_label = Label(entry, text=me.firstname+' '+me.name)
        name_label.config(padx=10, font=config.BOLD)
        name_label.grid(sticky=tk.W, row=0, column=0)


class PowerContentFrame(ContentFrame):
    def __init__(self, *args, **kwargs):
        ContentFrame.__init__(self, *args, **kwargs)
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=300)
        entry.pack(expand=True)
        self.disconnect_button = Button(entry, text='Disconnect', button_left='button_left_users')
        self.disconnect_button.bind("<Button-1>", lambda event, arg='disconnect': self.on_click(arg))
        self.disconnect_button.pack()
        self.quit_button = Button(entry, text='Quit', button_left='button_left_power')
        self.quit_button.bind("<Button-1>", lambda event, arg='quit': self.on_click(arg))
        self.quit_button.pack()
    
    def on_click(self, e):
        if e == 'disconnect':
            try:
                os.remove('ck.key')
                self.disconnect_button.update_right('button_right_tick')
                self.disconnect_button.update_text('Disconnected')
            except OSError:
                pass
        elif e == 'quit':
            self.quit()
            
    def add_entry(self, e):
        pass
            

class LoginContentFrame(ContentFrame):
    def __init__(self, *args, **kwargs):
        ContentFrame.__init__(self, *args, **kwargs)
        entry = tk.Frame(self)
        entry.config(bg=config.BGCOLOR, height=300)
        entry.pack()
        self.login_button = Button(entry, text='Proceed online', button_left='button_left_users')
        self.login_button.pack()
        self.step = tk.StringVar()
    
    def set_login_button(self, url):
        self.login_button.bind("<Button-1>", lambda event, arg=['go_online', url]: self.on_click(*arg))

    def on_click(self, e, url):
        if e == 'go_online':
            push_out = os.dup(2)
            os.close(2) ### Remove output from console
            os.open(os.devnull, os.O_RDWR)
            try:
                webbrowser.open(url)
            finally:
                os.dup2(push_out, 2) ### Restore normal output
            self.step.set('online')
            self.login_button.bind("<Button-1>", lambda event, arg=['continue', None]: self.on_click(*arg))
            self.login_button.update_text('Retry')
        elif e == 'continue':
            self.step.set('continue')
    
    def add_entry(self, e):
        pass
            

if __name__ == '__main__':

    app = GUI()
    app.run()

