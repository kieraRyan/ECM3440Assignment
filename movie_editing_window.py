
import tkinter
from tkinter import ttk
import sv_ttk
import cv2 as cv
import db_processor
import os
from PIL import Image, ImageTk
import numpy as np

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

        self.tab_headings = ['Scenes', 'Stills']

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
            self.tree.insert('', tkinter.END, values=item, iid= item[0])

    
        self.tree.bind('<<TreeviewSelect>>', self.scene_selected)
        self.tree.bind('<Button-1>', self.handle_click)
       
        # self.tree.selection_set(14)
        # self.tree.see(7)

        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(expand=True, fill="both")

        # making new frames / 'tabs' and adding to the notebook dynamically
        for heading in self.tab_headings:
            setattr(self, heading, ttk.Frame(self.notebook))
            self.notebook.add(getattr(self, heading), text= heading)

        for index in range(2):
            for heading in self.tab_headings:
                getattr(self, heading).columnconfigure(index, weight=1)
                getattr(self, heading).rowconfigure(index, weight=1)
        
        self.new_scene_btn = ttk.Button(self.Scenes, text ="New Scene", width = 10, command = self.create_new_scene)
        self.delete_scene_btn = ttk.Button(self.Scenes, text ="Delete Scene", width = 10, command = self.scene_selected)
        self.play_scene_btn = ttk.Button(self.Scenes, text ="Play Scene", width = 10, command = self.scene_selected)

        self.new_still_btn = ttk.Button(self.Stills, text ="Capture stills", width = 10, command = self.create_new_still)
        self.new_still_btn.state(["disabled"])
        self.cancelbtn = ttk.Button(self.Stills, text= "Exit", width=10, command = self.exit)
        
        self.new_scene_btn.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")
        self.delete_scene_btn.grid(row=1, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")
        self.play_scene_btn.grid(row=2, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")

        self.new_still_btn.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")
        self.cancelbtn.grid(row=1, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")
    
    def create_new_scene (self):
        # create new scene in db and grab the inserted info
        scene_info = db_processor.create_new_scene(self.movie_info[0], self.movie_info[1])

        # add scene to list in UI and select it for editing
        self.tree.insert('', tkinter.END, values= scene_info, iid= scene_info[0])
        self.tree.selection_set(scene_info[0])

    
    def create_new_still (self):
        cam = cv.VideoCapture(0)

        brightness = 2
        contrast = 1

        while True:
            ret, frame = cam.read()
             
            frame = cv.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness) 

            cv.imshow('New Still', frame)
    
            flipped = cv.flip(frame, 1)

            # cv.imshow('flipped', flipped)

            key_pressed = cv.waitKey(10)
            # esc key pressed
            if key_pressed%256 == 27:
                break
            # elif key_pressed==-1:  # normally -1 returned,so don't print it
            #     continue
            # else:
            #     print (key_pressed)
            # > key pressed
            elif key_pressed%256 == 46:
                brightness += 2
                print('brightness ' + str(brightness))
                # frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
            # < key pressed
            elif key_pressed%256 == 44:
                brightness -= 2
                print('brightness ' + str(brightness))
            # + key pressed
            elif key_pressed%256 == 61:
                contrast += 0.1
                print('contrast ' + str(contrast))
                # frame = cv.rotate(frame, cv.ROTATE_90_CLOCKWISE)
            # - key pressed
            elif key_pressed%256 == 45:
                contrast -= 0.1
                print('contrast ' + str(contrast))
                # frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)

            # # space bar clicked
            elif key_pressed%256 == 32:
                self.save_still(flipped)

        cam.release()
        cv.destroyAllWindows()

    def save_still (self, frame) :
        current_path = os.path.dirname(os.path.realpath(__file__))

        # calc folder path based on movie name
        print('trying to save scene ' + str(self.selected_scene_info))
        folder_path = self.movie_info[1]
       
       # calculate the name based on the still name
        img_name = db_processor.calculate_next_still_name(self.selected_scene_info[1])

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
    
    def scene_selected (self, event):
       # grab the selected record
        self.selected_scene_info = self.tree.item(self.tree.selection(), 'values')

        # enable the still creation button button as movie has been selected
        self.new_still_btn.state(["!disabled"])
    
    def handle_click(self, event):
        """Event method called when treeview clicked/ when user attempts to resize columns, which
        prevents this action."""
        # stop the columns from being resized
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def exit(self):
        """Event method that exits the program if "Cancel" button clicked"""
        self.window.destroy()
        exit()

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

        self.current_still_path = 'test.png'
        self.current_image = Image.open(self.current_still_path)

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.movie_info = movie_info
        self.columnconfigure(0, weight=1)

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

        # self.switch = ttk.Checkbutton(
        #     self.tab_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        # )
        # self.switch.grid(row=1, column=0, columnspan=2, pady=10)

        self.image = tkinter.Label(self.pane_1)
        self.image.pack()

        self.rotate_btn = ttk.Button(self.tab_1, text ="Rotate", width = 10, command = self.rotate_current_image)
        self.rotate_btn.grid(row=1, column=0, columnspan=1, pady=10)

        self.save_still = ttk.Button(self.tab_1, text ="Save Changes", width = 10, command = self.update_still)
        self.save_still.grid(row=1, column=3, columnspan=1, pady=10)

        self.load_image()
    
    def load_image (self):
        self.still = ImageTk.PhotoImage(self.current_image)

        self.image.configure(image= self.still)
        self.image.image = self.still

    def rotate_current_image (self):
        # self.current_still_path = 'Movie_2\Movie_2_1_1.png'
        # self.current_image = Image.open(self.current_still_path)
        rotated_image = self.current_image.rotate(90)

        self.current_image = rotated_image
        self.load_image()      
    
    def update_still (self):
        self.current_image.save(self.current_still_path)


