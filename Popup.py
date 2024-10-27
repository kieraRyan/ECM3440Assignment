import tkinter
from tkinter import ttk

class Popup:
    def __init__(self, parent_window, message: str, confirmation = None):
        """Creates popup window showing relevant message."""
        self.popup = tkinter.Toplevel(parent_window)
        self.popup.geometry('500x100')
        self.popup.resizable(0,0)

        message = tkinter.Label(self.popup, text = message)
        message.pack()

        ok_button = ttk.Button(self.popup, text= 'OK')
        ok_button.pack()
        ok_button.bind('<Button-1>', self.close_popup)

        if confirmation:
            self.add_confirmation()

    def close_popup(self, event):
        """Event method to close popup when OK button clicked"""
        self.user_decision = True
        self.popup.destroy()

    def cancel_popup(self, event):
        """Event method to cancel popup when Cancel button clicked"""
        self.user_decision = False
        self.popup.destroy()
    
    def add_confirmation (self):
        cancel_button = ttk.Button(self.popup, text= 'Cancel')
        cancel_button.pack()
        cancel_button.bind('<Button-1>', self.cancel_popup)

    def wait (self):
        self.popup.wait_window()