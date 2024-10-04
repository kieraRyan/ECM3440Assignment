
import cv2 as cv
import tkinter
from tkinter import ttk 
import sv_ttk
import movie_selection_window
import movie_editing_window


window= tkinter.Tk()
window.title('Home')
window.geometry("800x700+10+10")
window.resizable(0, 0)

# movie_selection_window.AppMain(window).pack(expand=True, fill ='both')
movie_selection_window.MovieSelectionWindow(window)
sv_ttk.set_theme("dark")
window.mainloop()