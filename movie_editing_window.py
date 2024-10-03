
import tkinter
from tkinter import ttk
import sv_ttk
import cv2 as cv
import db_processor
import os

class SceneSelection(ttk.PanedWindow):
    def __init__(self, parent, movie_info):
        super().__init__(parent)

        self.movie_info = movie_info

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.var = tkinter.IntVar(self, 47)

        self.scene_fields = ['Id', 'Name', 'Order']

        self.add_widgets()

    def add_widgets(self):
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.pane_1,
            columns=self.scene_fields,
            height=11,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.tree.yview)

        self.tree.pack(expand=True, fill="both")

        for heading in self.scene_fields:
            self.tree.column(heading, anchor="w", width=100) 
            self.tree.heading(heading, text=heading)

        tree_data = db_processor.get_scenes_for_movie(self.movie_info[0])

        for item in tree_data:
            self.tree.insert('', tkinter.END, values=item)

    
        self.tree.bind('<<TreeviewSelect>>', self.scene_selected)
        self.tree.bind('<Button-1>', self.handle_click)
       
        # self.tree.selection_set(14)
        # self.tree.see(7)

        # self.notebook = ttk.Notebook(self.pane_2)
        # self.notebook.pack(expand=True, fill="both")

        # for n in range(1, 4):
        #     setattr(self, f"tab_{n}", ttk.Frame(self.notebook))
        #     self.notebook.add(getattr(self, f"tab_{n}"), text=f"Tab {n}")

        # for index in range(2):
        #     self.tab_1.columnconfigure(index, weight=1)
        #     self.tab_1.rowconfigure(index, weight=1)

        # self.scale = ttk.Scale(
        #     self.tab_1,
        #     from_=100,
        #     to=0,
        #     variable=self.var,
        # )
        # self.scale.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")

        # self.progress = ttk.Progressbar(self.tab_1, value=0, variable=self.var, mode="determinate")
        # self.progress.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="ew")

        # self.switch = ttk.Checkbutton(
        #     self.tab_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        # )
        # self.switch.grid(row=1, column=0, columnspan=2, pady=10)
    
    def scene_selected (self):
        print('')
    
    def handle_click(self, event):
        """Event method called when treeview clicked/ when user attempts to resize columns, which
        prevents this action."""
        # stop the columns from being resized
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"

class AppMain (ttk.Frame):
      def __init__(self, window, movie_info):
        super().__init__(window, padding=15)
        for index in range(2):
            self.columnconfigure(index, weight=1)
            self.rowconfigure(index, weight=1)

        StillManagement(self, movie_info).grid(row=0, column=0, padx=(0, 10), pady=(0, 20), sticky="nsew")
        SceneSelection(self, movie_info).grid(row=0, column=3, rowspan=2, padx=10, pady=(10, 0), sticky="nsew")

class StillManagement (ttk.PanedWindow):
    def __init__(self, parent, movie_info):
        super().__init__(parent)

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.movie_info = movie_info
        self.columnconfigure(0, weight=1)

        self.still = tkinter.PhotoImage(file='test.png')
        self.image = tkinter.Label(self.pane_1, image=self.still)
        self.image.pack()
        self.image.img = self.still
            
        self.submitbtn = ttk.Button(self.pane_1, text ="Capture stills", width = 10, command = self.create_new_still)
        self.submitbtn.place(x = 70, y = 135)
        self.cancelbtn = ttk.Button(self.pane_1, text= "Cancel",width=10,command = self.exit)
        self.cancelbtn.place(x=160, y=135)

        self.var = tkinter.IntVar(self, 47)
        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(expand=True, fill="both")

        for n in range(1, 4):
            setattr(self, f"tab_{n}", ttk.Frame(self.notebook))
            self.notebook.add(getattr(self, f"tab_{n}"), text=f"Tab {n}")

        for index in range(2):
            self.tab_1.columnconfigure(index, weight=1)
            self.tab_1.rowconfigure(index, weight=1)

        self.scale = ttk.Scale(
            self.tab_1,
            from_=100,
            to=0,
            variable=self.var,
        )
        self.scale.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")

        self.progress = ttk.Progressbar(self.tab_1, value=0, variable=self.var, mode="determinate")
        self.progress.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="ew")

        self.switch = ttk.Checkbutton(
            self.tab_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        )
        self.switch.grid(row=1, column=0, columnspan=2, pady=10)
        

    def exit(self):
        """Event method that exits the program if "Cancel" button clicked"""
        self.window.destroy()
        exit()

    def create_new_still (self):
        cam = cv.VideoCapture(0)

        img_counter = 0

        while True:
            ret, frame = cam.read()
            cv.imshow('New Still', frame)
            #cv.imshow('Adjusted',drawonme)

            key_pressed = cv.waitKey(10)
            # esc key pressed
            if key_pressed%256 == 27:
                break
            # space bar clicked
            elif key_pressed%256 == 32:
                self.save_still(frame)
                
                img_counter += 1

        cam.release()
        cv.destroyAllWindows()

    def save_still (self, frame) :
        current_path = os.path.dirname(os.path.realpath(__file__))

        folder_path = self.movie_info[1]
       
        img_name = db_processor.calculate_next_still_name(self.movie_info[1])

        # save the file in a specific folder related to the movie
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            print(f"Folder '{folder_path}' created.")

        os.chdir(folder_path)
        success = cv.imwrite(img_name, frame)
        if not success:
            print("Error saving image")
        
        # change directory back to og
        os.chdir(current_path)

        # save image to db now
        db_processor.create_new_still(img_name, self.movie_info[0], 1, folder_path)
    
    def login_unsuccessful_popup(self):
        """Creates an 'unsucessful login' popup screen in the case of exception when trying to authenticate 
        with the database."""
        self.popup = tkinter.Toplevel(self.window)
        self.popup.geometry('500x100')
        self.popup.resizable(0,0)
        errorMessage= ttk.Label(self.popup, text = "Login unsuccessful")
        errorMessage.pack()
        escape_button = ttk.Button(self.popup, text= 'OK')
        escape_button.pack()
        escape_button.bind('<Button-1>', self.close_popup)

    def close_popup(self, event):
        """Popup if closed when OK button selected"""
        self.popup.destroy()


