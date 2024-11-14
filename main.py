
import tkinter
import sv_ttk
import movie_selection_window

window= tkinter.Tk()
window.title('Home')
window.geometry("800x700+10+10")
window.resizable(0, 0)

movie_selection_window.MovieSelectionWindow(window)
sv_ttk.set_theme("dark")
window.mainloop()