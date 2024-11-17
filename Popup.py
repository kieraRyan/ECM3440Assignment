import tkinter
from tkinter import ttk

class Popup:
    def __init__(self, parent_window: ttk.Frame, message: str, confirmation = None) -> None:
        """
        Creates a popup window with a defined message
        OK and Cancel buttons created depending on input parameters

        Parameters:
            parent_window (ttk.Frame): Parent window in which the popup should be placed on/ tied to
            message (str): The message to be displayed in the popup
            confirmation (bool): Option parameter indicating whether the popup should provide an option to confirm/ cancel an action

        Returns: None
        """
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

    def close_popup(self, event: object) -> None:
        """
        Event method to close popup when OK button clicked

        Parameters:
            event (obj): The user action which has triggered the function

        Returns: None
        """
        self.user_decision = True
        self.popup.destroy()

    def cancel_popup(self, event):
        """
        Event method to cancel popup when Cancel button clicked
        
        Parameters:
            event (obj): The user action which has triggered the function

        Returns: None
        """
        self.user_decision = False
        self.popup.destroy()
    
    def add_confirmation (self):
        """
        Method to add Cancel button to popup window if confirmation = True
        
        Parameters: None

        Returns: None
        """
        cancel_button = ttk.Button(self.popup, text= 'Cancel')
        cancel_button.pack()
        cancel_button.bind('<Button-1>', self.cancel_popup)

    def wait (self):
        """
        Adds wait condition to popup window tso that calling window waits until this widget is destroyed before continuing
        
        Parameters: None

        Returns: None
        """
        self.popup.wait_window()