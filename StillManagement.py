
import tkinter
from tkinter import ttk
from PIL import Image, ImageTk, ImageEnhance

class StillManagement (ttk.PanedWindow):
    def __init__(self, parent, movie_info):
        super().__init__(parent)

        self.parent_window = parent

        self.current_image = Image.open(self.parent_window.current_still_path)

        self.pane_1 = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.pane_2 = ttk.Frame(self, padding=(0, 10, 5, 0))
        self.add(self.pane_1, weight=1)
        self.add(self.pane_2, weight=3)

        self.movie_info = movie_info
        self.columnconfigure(0, weight=1)

        self.var = tkinter.IntVar(self, 47)
        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(expand=True, fill="both")

        self.tab_headings = ['Play', 'Editing', 'Brightness']

        for heading in self.tab_headings:
            setattr(self, heading, ttk.Frame(self.notebook))
            self.notebook.add(getattr(self, heading), text= heading)

        for index in range(2):
            for heading in self.tab_headings:
                getattr(self, heading).columnconfigure(index, weight=1)
                getattr(self, heading).rowconfigure(index, weight=1)

        self.scale = ttk.Scale(
            self.Play,
            from_=100,
            to=0,
            variable=self.var,
        )
        
        self.scale.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="ew")

        self.progress = ttk.Progressbar(self.Play, value=0, variable=self.var, mode="determinate")
        self.progress.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="ew")

        self.save_still = ttk.Button(self.Play, text ="Save Changes", width = 15, command = self.update_still)
        self.save_still.grid(row=1, column=0, columnspan=2, pady=10)

        # self.switch = ttk.Checkbutton(
        #     self.tab_1, text="Dark theme", style="Switch.TCheckbutton", command=sv_ttk.toggle_theme
        # )
        # self.switch.grid(row=1, column=0, columnspan=2, pady=10)

        self.image = tkinter.Label(self.pane_1)
        self.image.pack()

        self.sharpness_label = tkinter.Label(self.Editing, text='Sharpness: 0')
        self.sharpness_label.grid(row=1, column=0,  padx=(20, 10), pady=(20, 10), sticky="ew")
        self.sharpness_val = tkinter.IntVar(self, 0)
        self.sharpness_slider = ttk.Scale(
            self.Editing,
            from_=-2.0,
            to= 5.0,
            variable=self.sharpness_val,
            command= self.change_sharpness
        )
        self.sharpness_slider.grid(row=0, column=0, padx=(10, 20), pady=(20, 10), sticky="ew")

        self.rotate_btn = ttk.Button(self.Editing, text ="Rotate", width = 10, command = self.rotate_current_image)
        self.rotations = 0
        self.rotate_btn.grid(row=0, column=1, pady=10)
        self.flip_btn = ttk.Button(self.Editing, text ="Flip", width = 10, command = self.flip_current_image)
        self.image_flipped = False
        self.flip_btn.grid(row=1, column=1, pady=10)


        self.brightness_label = tkinter.Label(self.Brightness, text='Brightness: 50%')
        self.brightness_label.grid(row=1, column=0,  padx=(20, 10), pady=(20, 10), sticky="ew")

        self.brightness_val = tkinter.IntVar(self, 50)
        self.brightness_slider = ttk.Scale(
            self.Brightness,
            from_=0,
            to=100,
            variable=self.brightness_val,
            command= self.change_brightness
        )
        self.brightness_slider.grid(row=0, column=0, padx=(10, 20), pady=(20, 10), sticky="ew")

        self.contrast_label = tkinter.Label(self.Brightness, text='Contrast: 50%')
        self.contrast_label.grid(row=1, column=1,  padx=(20, 10), pady=(20, 10), sticky="ew")
        self.contrast_val = tkinter.IntVar(self, 50)
        self.contrast_slider = ttk.Scale(
            self.Brightness,
            from_=0,
            to= 100,
            variable=self.contrast_val,
            command= self.change_contrast
        )
        self.contrast_slider.grid(row=0, column=1, padx=(10, 20), pady=(20, 10), sticky="ew")

        self.load_image()
    
    def load_image (self):
        self.still = ImageTk.PhotoImage(self.current_image)

        self.image.configure(image= self.still)
        self.image.image = self.still

    def rotate_current_image (self):
        # keep track of rotations for when we do image processing later
        self.rotations += 1
        self.current_image = self.current_image.rotate(90)
        self.load_image()      
    
    def flip_current_image (self):
        # track whether the image has been flipped for when we do image processing
        self.image_flipped = not self.image_flipped
        self.current_image = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.load_image()

    def transform_image(self):
        # grab original image so that we dont transform the current morphed image - need to use our og image as a base
        self.current_image = Image.open(self.parent_window.current_still_path)
        # set image brightness
        brightness_percent = ((self.brightness_val.get() - 50) / 100) + 1
        enhancer = ImageEnhance.Brightness(self.current_image)
        self.current_image = enhancer.enhance(brightness_percent)

        # set sharpness
        enhancer = ImageEnhance.Sharpness(self.current_image)
        self.current_image = enhancer.enhance(self.sharpness_val.get())

        # set contrast
        contrast_percent = ((self.contrast_val.get() - 50) / 100) + 1
        enhancer = ImageEnhance.Contrast(self.current_image)
        self.current_image = enhancer.enhance(contrast_percent)

        # reapply any flipping/ orientation changes
        if self.image_flipped:
            self.current_image = self.current_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        
        # if not a full circle rotation
        if self.rotations % 4 != 0:
            for i in range((self.rotations % 4)):
                self.current_image = self.current_image.rotate(90)

        self.load_image()

    def change_brightness (self, event):
        # update the brightness label
        self.brightness_label.config(text = f"Brightness: {int(self.brightness_slider.get())}%")
        self.transform_image()
    
    def change_sharpness (self, event):
        self.sharpness_label.config(text = f"Sharpness: {int(self.sharpness_slider.get())}")
        self.transform_image()
    
    def change_contrast (self, event):
        self.contrast_label.config(text = f"Contrast: {int(self.contrast_slider.get())}%")
        self.transform_image()

    def update_still (self):
        self.current_image.save(self.parent_window.current_still_path)


