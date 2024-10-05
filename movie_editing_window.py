from tkinter import ttk
import StillManagement as sm
import SceneSelection as ss

class AppMain (ttk.Frame):
      def __init__(self, window, movie_info):
        super().__init__(window, padding=15)
        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)

        sm.StillManagement(self, movie_info).grid(row=0, column=0, padx=(0, 10), pady=(0, 20), sticky="nsew")
        ss.SceneSelection(self, movie_info).grid(row=0, column=3, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")
