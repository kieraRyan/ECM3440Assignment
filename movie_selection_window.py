import tkinter
from tkinter import ttk
import db_processor
import movie_editing_window
import sv_ttk
import cv2
from Popup import Popup

class MovieSelectionWindow:

    def __init__(self, win):
        """On initialisation, engine and window parameters assigned to attributes for ease of access
        required tkinter widgets created and placed on screen, variable names for the entry fields defined
        in an array, along with the headings for the treeview. retrieve_movie_list called to create 
        treeview object and populate with correct data."""
        self.title = tkinter.Label(win, text = 'Please select a movie or create a new movie')

        self.movie_field_names = ['id', 'name', 'filePath']
        self.movie_field_labels = ['Id', 'Name', 'File Path']
        self.selectedRecord = ['','','']
        self.win = win
        #self.engine = engine

        # create all the buttons amd bind to events
        self.edit_movie_button = ttk.Button(win, text= 'Edit', width = 15, command =self.edit_movie)
        self.edit_movie_button.state(["disabled"])
        self.new_movie_button = ttk.Button(win, text= 'New Movie', width = 15, command =self.add_movie)
        self.export_movie_button = ttk.Button(win, text= 'Download as Movie file', width = 15, command =self.export_movie)
        self.export_movie_button.state(["disabled"])
        self.exit_button = ttk.Button(win, text= 'Exit', width = 15, command =self.exit)
        
        # create list of movies
        self.movies = self.retrieve_movie_list()

        # place all widgets
        self.title.place(x= 20, y=20)

        self.new_movie_button.place(x=450, y=100)
        self.edit_movie_button.place(x=450, y=200)
        self.export_movie_button.place(x= 450, y=300)
        self.exit_button.place(x= 450, y=400)

        self.movies.place(x = 20, y= 50)

    def retrieve_movie_list(self):
        """Creates a treeview object with columns equal to the names of the fields specified in
        movie_field_labels array. Headings populated using the same array. Manual configuration of
        width of certain headings necessary. Pandas dataframe used to execute and recieve results of raw sql 
        query that displays customer/ contact information - found that raw sql had fastest execution time.
        Results displayed in treeview, which is output back to initialisation method.."""
        # create treeview object and populate with customer data
        movies = ttk.Treeview(self.win,columns= self.movie_field_labels, show = 'headings', height = 20)
        movies.bind('<<TreeviewSelect>>', self.select_customer)
        movies.bind('<Button-1>', self.handle_click)
        # add headings to the columns
        for heading in self.movie_field_labels:
            movies.column(heading, width=65) 
            movies.heading(heading, text=heading)
        # (manual configuration of width needed for some)
        movies.column('Id', width=30)
        movies.column('Name', width=100)
        movies.column('File Path', width=250)
        self.win.update()

        # retrieve data and populate into treeview
        data_list = db_processor.get_all_movies()
        for record in data_list:
            movies.insert('', tkinter.END, values=record)
        
        return movies
    
    def select_customer(self, event):
        self.selectedRecord = self.movies.item(self.movies.focus(), 'values')

        # enable the edit/ export buttons as movie has been selected
        self.edit_movie_button.state(["!disabled"])
        self.export_movie_button.state(["!disabled"])
    
    def handle_click(self, event):
        """Event method called when treeview clicked/ when user attempts to resize columns, which
        prevents this action."""
        # stop the columns from being resized
        if self.movies.identify_region(event.x, event.y) == "separator":
            return "break"

    def add_movie(self):
        """Directs back to main program to create new customer window, passing in the db engine, 
            and the current customer_list object."""
        # initialise add customer window
        movie_info = db_processor.create_new_movie()
        self.create_new_window(movie_info)
    
    def edit_movie (self):
        self.create_new_window([self.selectedRecord[0], self.selectedRecord[1]])
       
    def create_new_window (self, window_info):
        self.win.destroy()

        window= tkinter.Tk()
        window.title(window_info[1])
        window.geometry("1000x650+10+10")
        # window.resizable(0, 0)

        movie_editing_window.MovieEditingWindow(window, window_info).pack(expand=True, fill ='both')
        sv_ttk.set_theme("dark")
        window.mainloop()

    def exit(self):
        """Event method that closes window/ program when exit button selected"""
        self.win.destroy()
        exit()       
    
    def export_movie(self):
        
        image_folder = self.selectedRecord[1]
        video_name = f'{image_folder}.avi'
        
        still_paths = db_processor.get_movie_stills_in_order(self.selectedRecord[0])
        images = [img[0] for img in still_paths]
        
        frame = cv2.imread(images[0])
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, 0, 6, (width,height))

        for image in images:
            video.write(cv2.imread(image))

        cv2.destroyAllWindows()
        video.release()

        Popup(self.win, 'Movie created and saved to movies folder')