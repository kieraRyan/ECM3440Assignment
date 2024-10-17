import tkinter
from tkinter import ttk
import cv2 as cv
import db_processor
import os
import numpy as np
from StillManagement import StillManagement
from PIL import Image

class SceneSelection(ttk.PanedWindow):
    def __init__(self, parent, movie_info, still_window: StillManagement):
        super().__init__(parent)

        self.parent_window = parent
        # whilst i dont like it, we need some way of accessing neighbouring class...
        self.still_window = still_window
        self.movie_info = movie_info

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.var = tkinter.IntVar(self, 47)

        self.scene_fields = ['Id', 'Scenes', 'Order']
        self.still_fields = ['Id', 'Stills', 'Order']

        self.tab_headings = ['Scenes', 'Stills']

        self.add_widgets()

    def add_widgets(self):
        self.scrollbar = ttk.Scrollbar(self.pane_1)

        self.scene_tree = ttk.Treeview(
            self.pane_1,
            columns=self.scene_fields,
            height=6,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.scene_tree.yview)

        self.scene_tree.pack(expand=True, fill="both")

        for heading in self.scene_fields:
            self.scene_tree.column(heading, anchor="w", width=100) 
            self.scene_tree.heading(heading, text=heading)

        tree_data = db_processor.get_scenes_for_movie(self.movie_info[0])
        for item in tree_data:
            self.scene_tree.insert('', tkinter.END, values=item, iid= item[0])
        
        self.scene_tree.bind('<<TreeviewSelect>>', self.scene_selected)
        self.scene_tree.bind('<Button-1>', self.handle_click)

        # scrollbars
        self.still_scrollbar = ttk.Scrollbar(self.pane_1)
        self.still_scrollbar.pack(side="right", fill="y")
        self.scrollbar.pack(side="right", fill="y")

        self.still_tree = ttk.Treeview(
            self.pane_1,
            columns=self.still_fields,
            height=6,
            selectmode="browse",
            show=("headings",),
            yscrollcommand=self.still_scrollbar.set,
        )
        
        self.still_scrollbar.config(command=self.still_tree.yview)

        self.still_tree.pack(expand=True, fill="both")

        for heading in self.still_fields:
            self.still_tree.column(heading, anchor="w", width=100) 
            self.still_tree.heading(heading, text=heading)
        
        self.still_tree.bind('<<TreeviewSelect>>', self.still_selected)
        self.still_tree.bind('<Button-1>', self.handle_click)

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
        self.scene_tree.insert('', tkinter.END, values= scene_info, iid= scene_info[0])
        self.scene_tree.selection_set(scene_info[0])

    
    def create_new_still (self):
        cam = cv.VideoCapture(0)

        # default picture settings
        brightness = 2
        contrast = 1
        flipped = False
        sharp = False
        rotation_angle = 0

        while True:
            ret, frame = cam.read()

            # adjusting brightness and contrast
            frame = cv.addWeighted(frame, contrast, np.zeros(frame.shape, frame.dtype), 0, brightness)

            # sharpening image
            if sharp:
                # Create the sharpening kernel 
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 
                frame = cv.filter2D(frame, -1, kernel) 
            
            # if flipped is True, flip on the y axis
            if flipped:
                frame = cv.flip(frame, 1)

            # grab dimensions of image and locate center
            (h, w) = frame.shape[:2]
            (cX, cY) = (w // 2, h // 2)
            # rotate our image by 45 degrees around the center of the image
            matrix = cv.getRotationMatrix2D((cX, cY), rotation_angle, 1.0)
            frame = cv.warpAffine(frame, matrix, (w, h))

            cv.imshow('New Still', frame)

            key_pressed = cv.waitKey(10)
            # esc key pressed
            if key_pressed%256 == 27:
                break
            # > key pressed
            elif key_pressed%256 == 46:
                brightness += 5

            # < key pressed
            elif key_pressed%256 == 44:
                brightness -= 5

            # + key pressed
            elif key_pressed%256 == 61:
                contrast += 0.1

            # - key pressed
            elif key_pressed%256 == 45:
                contrast -= 0.1

            # any arrow key pressed
            elif key_pressed%256 == 0:
                # rotate by 90 degrees
                rotation_angle += 90

            # enter key pressed
            elif key_pressed%256 == 13:
                # flip image horizontally
                flipped = not flipped

            # s key pressed
            elif key_pressed%256 == 115:
                sharp = not sharp

            # space bar clicked
            elif key_pressed%256 == 32:
                self.save_still(frame)

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

        file_path = folder_path + '/' + img_name
        print(file_path)

        # save image to db now
        db_processor.create_new_still(img_name, self.selected_scene_info[0], file_path)

        self.load_new_image_on_neighbour(file_path)
        self.update_still_data()

    def load_new_image_on_neighbour (self, file_path):
        # update displayed image path in parent object and force refresh on neighbouring class
        self.parent_window.current_still_path = file_path
        self.still_window.current_image = Image.open(self.parent_window.current_still_path)
        # reset editing controls when new image loaded
        self.still_window.default_editing_values()
        self.still_window.default_label_values()
        self.still_window.load_image()
    
    def scene_selected (self, event):
       # grab the selected record
        self.selected_scene_info = self.scene_tree.item(self.scene_tree.selection(), 'values')

        # unselect any stills
        if len(self.still_tree.selection()) > 0:
            self.still_tree.selection_remove(self.still_tree.selection()[0])

        self.update_still_data()

        # enable the still creation button button as scene has been selected
        self.new_still_btn.state(["!disabled"])
    
    def update_still_data(self):
        # STILL.id, STILL.name, SCENE.id AS scene_id, STILL."order", STILL.filePath
        # (16, 'Movie_2_6_16.png', 6, 2, 'Movie_2/Movie_2_6_16.png')
        self.still_data = db_processor.get_stills_for_scene(self.selected_scene_info[0])

         # clear the still treeview child data
        for item in self.still_tree.get_children():
            self.still_tree.delete(item)

        # add stills from newly selected scene to treeview
        for item in self.still_data:
            self.still_tree.insert('', index="end", iid= item[0], values= [item[0], item[1], item[3]])

        # update on parent window for playing later
        self.parent_window.stills_to_play = self.still_data

    def still_selected (self, event):
       # grab the selected record and its filepath
       self.selected_still_info = self.still_tree.item(self.still_tree.selection(), 'values')
       path = ''
       for still in self.still_data:
            if (str(still[0]) == str(self.selected_still_info[0])):
                path = still[4]

       self.load_new_image_on_neighbour(path)
    
    def handle_click(self, event):
        """Event method called when treeview clicked/ when user attempts to resize columns, which
        prevents this action."""
        # stop the columns from being resized
        if self.scene_tree.identify_region(event.x, event.y) == "separator":
            return "break"
    
    def exit(self):
        """Event method that exits the program if "Cancel" button clicked"""
        self.window.destroy()
        exit()