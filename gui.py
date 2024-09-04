from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label, messagebox, OptionMenu, StringVar
from PIL import Image, ImageTk
import cv2
import threading
import sys
import numpy as np

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/melodyflavel/Projects/Python/Reform/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class GUI:

    def __init__(self):
        self.window = Tk()
        # Placeholder size to be overridden by subclasses.
        self.window.geometry("100x100")
        self.window.configure(bg = "#F3F3F3")
        self.canvas = Canvas(
            self.window,
            bg = "#F3F3F3",
            # Placeholder values to be overridden by subclasses.
            height = 0,
            width = 0,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.window.resizable(False, False)

class Launch(GUI):

    def __init__(self):
        super().__init__()
        self.window.geometry("500x420")
        self.canvas.config(height=420, width=500)
        self.entry_image = None  # Declare an attribute to store image references
        self.launch_button_image = None  # Declare an attribute to store image references
        self.display()

    def display(self):
        self.canvas.place(x = 0, y = 0)

        self.entry_image = PhotoImage(file=relative_to_assets("entry_1.png"))
        self.launch_button_image = PhotoImage(file=relative_to_assets("launch_button.png"))

        self.canvas.create_text(
            30.0,
            20.0,
            anchor="nw",
            text="""Hi! I’m here to help analyze your exercise form and provide real-time feedback on
areas that could use improvement. My assessments are grounded in widely 
recognized standards for proper form during these exercises.

Please note that my analysis focuses on the conventional execution of exercises 
and does not consider variations such as sumo styles or close-foot stances. The 
depth and accuracy of the analysis are subject to the constraints of the MediaPipe 
pose estimation models.

To ensure an accurate assessment, please make sure your video meets the 
following criteria:
	• The video shows one complete repetition of the exercise.
	• The video is clear and well-lit.
	• Your entire body is visible within the frame.
	• There are no objects or obstructions blocking the camera's view.
	• The video begins with you in the starting position.""",
            fill="#000000",
            font=("ArialMT", 12 * -1)
        )

        self.canvas.create_text(
            35.0,
            275.0,
            anchor="nw",
            text="Exercise",
            fill="#000000",
            font=("ArialMT", 16 * -1)
        )

        # Exercise selection menu.
        self.selected_exercise = StringVar(self.window)
        self.selected_exercise.set("Select")

        exercise_menu = OptionMenu(
            self.window, 
            self.selected_exercise, 
            "Squat", "Deadlift"
        )
        exercise_menu.place(
            x=35.0,
            y=305.0,
            width=80.0,
            height=30.0
        )

        exercise_menu.configure(
            bg="#F3F3F3",
            fg="#000000",
            activebackground="#000000",
            highlightthickness=0
        )

        self.canvas.create_text(
            140.0,
            275.0,
            anchor="nw",
            text="Video Path",
            fill="#000000",
            font=("ArialMT", 16 * -1)
        )
        video_path_entry_bg = self.canvas.create_image(
            298.0,
            320.0,
            image=self.entry_image
        )
        self.video_path_entry = Entry(
            bd=0,
            bg="#E6E6E6",
            fg="#000716",
            highlightthickness=0
        )
        self.video_path_entry.place(
            x=145.0,
            y=305.0,
            width=306.0,
            height=30.0
        )

        launch_button = Button(
            image=self.launch_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=self.store_values,
            relief="flat",
            bg="#FFFFFF",      
            activebackground="#FFFFFF"
        )
        launch_button.place(
            x=136.0,
            y=360.0,
            width=229.0,
            height=39.0
        )
        self.window.resizable(False, False)
        self.window.mainloop()

    def store_values(self):
        self.exercise = self.selected_exercise.get()
        self.video_path = self.video_path_entry.get()
        self.window.destroy()
    
    def get_values(self):
        return self.exercise, self.video_path
    
    def show_selection_error(self):
        messagebox.showerror("Error", "Please select an exercise from the drop down menu.")
    
class Analysis(GUI):

    def __init__(self):
        super().__init__()
        self.window.geometry("1000x500")
        self.canvas.config(height=500, width=1000)
        self.images = {
            "cross": relative_to_assets("cross.png"),
            "exclamation_mark": relative_to_assets("exclamation_mark.png"),
            "check_mark": relative_to_assets("check_mark.png")
        }
        self.text = {}
        # Label to display the original video.
        self.original_video_label = Label(self.window)
        self.original_video_label.place(x=0, y=0)
        # Label to display the annotated video.
        self.processed_video_label = Label(self.window)
        self.processed_video_label.place(x=(959 - 651), y=0)

        self.analysis = None

    def display(self, analysis):
        self.analysis = analysis
        self.canvas.place(x = 0, y = 0)
        
        background_image = PhotoImage(file=relative_to_assets("grey_rectangle.png"))
        self.canvas.create_image(
            651 + (308 / 2),  
            170,
            image=background_image,
            anchor="center"
        )
    
        # Ensure the image is not garbage collected.
        self.canvas.background_image = background_image

        # Create the custom button icons.
        replay_icon = PhotoImage(file=relative_to_assets("replay_button.png"))
        change_icon = PhotoImage(file=relative_to_assets("change_button.png"))
        exit_icon = PhotoImage(file=relative_to_assets("exit_button.png"))

        # Replay button.
        replay_label = Label(self.window, image=replay_icon, bg="#F3F3F3")
        replay_label.place(x=650, y=420, width=100, height=50)
        replay_label.bind("<Button-1>", lambda e: self.replay_video())

        # Change button.
        change_label = Label(self.window, image=change_icon, bg="#F3F3F3")
        change_label.place(x=760, y=420, width=100, height=50)
        change_label.bind("<Button-1>", lambda e: self.change_video())

        # Exit button.
        exit_label = Label(self.window, image=exit_icon, bg="#F3F3F3")
        exit_label.place(x=870, y=420, width=100, height=50)
        exit_label.bind("<Button-1>", lambda e: self.exit_app())

        # Ensure the images are not garbage collected.
        replay_label.image = replay_icon
        change_label.image = change_icon
        exit_label.image = exit_icon

        self.window.resizable(False, False)
        self.window.mainloop()
                
    # Replay the video if the 'Replay' button is clicked.
    def replay_video(self):
        if not self.analysis.is_playing:  # Check if a video is already playing.
            self.analysis.is_playing = True
            threading.Thread(target=self.analysis.process_video, args=(self,), daemon=True).start()
            self.display(self.analysis)

    def exit_app(self):
        sys.exit(0)

    def change_video(self):
        self.window.destroy()
        import main
        main.main()

    def update_analysis_text(self):

        # Clear previous text.
        self.canvas.delete("analysis_text")

        if self.analysis.exercise == "squat":
            if self.analysis.view == "left" or self.analysis.view == "right":
                # Update torso analysis text.
                self.text["Torso"] = "Torso position is adequate."
                self.update_result_image("check_mark", 80)
                if self.analysis.results.get("torso", {}).get("current", 0) == "upright":
                    self.text["Torso"] = "The torso is too upright."
                    self.update_result_image("cross", 80)
                elif self.analysis.results.get("torso", {}).get("current", 0) == "forward":
                    self.text["Torso"] = "The torso is leaning too far forward."
                    self.update_result_image("cross", 80)

                # Update depth analysis text.
                self.text["Depth"] = "Squat depth is adequate."
                self.update_result_image("check_mark", 164)
                if self.analysis.results.get("depth", {}).get("current", 0) == "shallow":
                    self.text["Depth"] = "The squat is not deep enough."
                    self.update_result_image("exclamation_mark", 164)
                elif self.analysis.results.get("depth", {}).get("current", 0) == "deep":
                    self.text["Depth"] = "The squat is too deep."
                    self.update_result_image("cross", 164)

                if self.analysis.weight["type"] == "barbell":
                    # Update barbell path analysis text.
                    self.text["Barbell"] = "Your barbell path is straight."
                    self.update_result_image("check_mark", 245)
                    if self.analysis.results.get("barbell", {}).get("straight", False) == False:
                        self.text["Barbell"] = "Your barbell path is not straight."
                        self.update_result_image("cross", 245)

            elif self.analysis.view == "front":
                # Update feet.
                self.text["Feet"] = "Your foot stance is adequate."
                self.update_result_image("check_mark", 80)
                if self.analysis.results.get("feet", {}).get("current", 0) == "far":
                    self.text["Feet"] = "Your feet are too far apart."
                    self.update_result_image("cross", 80)
                elif self.analysis.results.get("torso", {}).get("current", 0) == "close":
                    self.text["Feet"] = "Your feet are too close together."
                    self.update_result_image("cross", 80)

                # Update toes.
                self.text["Toes"] = "Your toes are adequately pointed outward."
                self.update_result_image("check_mark", 164)
                if self.analysis.results.get("right_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "outward":
                    self.text["Toes"] = "Your toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "inward":
                    self.text["Toes"] = "Your toes are not pointed outward enough."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your right toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your right toes are not pointed outward enough."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("left_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("right_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your left toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("left_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("right_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your left toes are not pointed outward enough."
                    self.update_result_image("cross", 164)

                self.text["Knees"] = "Knees are adequately positioned."
                self.update_result_image("check_mark", 245)
                print(f"{self.analysis.results.get("right_knee", {}).get("current", 0)}")
                if self.analysis.results.get("right_knee", {}).get("current", 0) == "inward" and self.analysis.results.get("left_knee", {}).get("current", 0) == "inward":
                    self.text["Knees"] = "Both knees are moving inward."
                    self.update_result_image("cross", 245)
                elif self.analysis.results.get("right_knee", {}).get("current", 0) == "inward" and self.analysis.results.get("left_knee", {}).get("current", 0) == "adequate":
                    self.text["Knees"] = "Right knee is moving inward."
                    self.update_result_image("cross", 245)
                elif self.analysis.results.get("right_knee", {}).get("current", 0) == "adequate" and self.analysis.results.get("left_knee", {}).get("current", 0) == "inward":
                    self.text["Knees"] = "Left knee is moving inward."
                    self.update_result_image("cross", 245)
            
        elif self.analysis.exercise == "deadlift":
            if self.analysis.view == "left" or self.analysis.view == "right":
                
                # Update torso analysis text.
                self.text["Hips"] = "Your hip placement is adequate."
                self.update_result_image("check_mark", 80)
                if self.analysis.results.get("hips", {}).get("current", 0) == "high":
                    self.text["Hips"] = "Your hips are above your shoulders."
                    self.update_result_image("cross", 80)

                # Update depth analysis text.
                self.text["Back"] = "Your back extension is adequate."
                self.update_result_image("check_mark", 164)
                if self.analysis.results.get("back", {}).get("overextended", 0) == True:
                    self.text["Back"] = "Your back is overextended at the peak\nof the deadlift."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("back", {}).get("current", 0) == "overflexed":
                    self.text["Back"] = "Your back is overflexed at the peak\nof the deadlift."
                    self.update_result_image("cross", 164)

                if self.analysis.weight["type"] == "barbell":
                    # Update barbell path analysis text.
                    self.text["Barbell"] = "Your barbell path is straight."
                    self.update_result_image("check_mark", 245)
                    if self.analysis.results.get("barbell", {}).get("straight", False) == False:
                        self.text["Barbell"] = "Your barbell path is not straight."
                        self.update_result_image("cross", 245)

            elif self.analysis.view == "front":

                # If a different view ('left' or 'right') was detected before detecting this view
                # ('front'), remove the previous key-value pairs from the 'text' dictionary so that 
                # only the key-value pairs from this view ('front') are displayed.
                self.text.pop("Hips", None)
                self.text.pop("Back", None)
                self.text.pop("Barbell", None)

                # Update feet.
                self.text["Feet"] = "Your foot stance is adequate."
                self.update_result_image("check_mark", 80)
                if self.analysis.results.get("feet", {}).get("current", 0) == "far":
                    self.text["Feet"] = "Your feet are too far apart."
                    self.update_result_image("cross", 80)
                elif self.analysis.results.get("feet", {}).get("current", 0) == "close":
                    self.text["Feet"] = "Your feet are too close together."
                    self.update_result_image("cross", 80)

                # Update toes.
                self.text["Toes"] = "Your toes are adequately pointed outward."
                self.update_result_image("check_mark", 164)
                if self.analysis.results.get("right_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "outward":
                    self.text["Toes"] = "Both of your toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "inward":
                    self.text["Toes"] = "Both of your toes are not pointed outward\nenough."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your right toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("right_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("left_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your right toes are not pointed outward enough."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("left_toes", {}).get("current", 0) == "outward" and self.analysis.results.get("right_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your left toes are pointed too outward."
                    self.update_result_image("cross", 164)
                elif self.analysis.results.get("left_toes", {}).get("current", 0) == "inward" and self.analysis.results.get("right_toes", {}).get("current", 0) == "adequate":
                    self.text["Toes"] = "Your left toes are not pointed outward enough."
                    self.update_result_image("cross", 164)

        text_list = list(self.text.items())
        if len(self.text) > 0:
            first_key, first_value = text_list[0]
        if len(self.text) > 1:
            second_key, second_value = text_list[1]
        if len(self.text) > 2:
            third_key, third_value = text_list[2]

        if len(self.text) > 0:
            self.canvas.create_text(
                711.0,
                71.0,
                anchor="nw",
                text=first_key,
                fill="#000000",
                font=("Arial BoldMT", 16 * -1),
                tags="analysis_text"
            )

            self.canvas.create_text(
                711.0,
                94.0,
                anchor="nw",
                text=first_value,
                fill="#000000",
                font=("ArialMT", 12 * -1),
                tags="analysis_text"
            )
        if len(self.text) > 1:
            self.canvas.create_text(
                711.0,
                155.0,
                anchor="nw",
                text=second_key,
                fill="#000000",
                font=("ArialMT", 16 * -1),
                tags="analysis_text"
            )

            self.canvas.create_text(
                713.0,
                178.0,
                anchor="nw",
                text=second_value,
                fill="#000000",
                font=("ArialMT", 12 * -1),
                tags="analysis_text"
            )
        if len(text_list) > 2:
            self.canvas.create_text(
                711.0,
                237.0,
                anchor="nw",
                text=third_key,
                fill="#000000",
                font=("ArialMT", 16 * -1),
                tags="analysis_text"
            )
            self.canvas.create_text(
                711.0,
                260.0,
                anchor="nw",
                text=third_value,
                fill="#000000",
                font=("ArialMT", 12 * -1),
                tags="analysis_text"
            )
        self.window.update_idletasks()


        # Ensure the canvas is updated.
        self.window.update_idletasks()
        #self.update_result_image(self.analysis)

    def update_result_image(self, image_key, y_position):
        image_path = self.images.get(image_key)
        image = PhotoImage(file=image_path)
        # Positions for the images next to each analysis criterion.
        x_position = 684.0
        # Remove previous images.
        self.canvas.delete("result_image")
            
        # Place the image in the corresponding position with a unique tag.
        self.canvas.create_image(
            (x_position, y_position),
            image=image,
            tags=f"image"
        )
        
        # Reference to avoid garbage collection.
        setattr(self, f"{y_position}_image", image)


    def update_video_frame(self, frame, label):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame_rgb.shape[:2]
        max_height = 500
        max_width = 959 - 651
        scale = max_height / height
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
        # Create a new image with a white background (change the color here)
        canvas_image = np.ones((max_height, max_width, 3), dtype=np.uint8) * 255  # 255 for white background
        # Crop the frame evenly from left and right if it exceeds 'max_width'.
        if new_width > max_width:
            excess_width = new_width - max_width
            # Calculate cropping boundaries.
            start_x = excess_width // 2
            end_x = start_x + max_width
            frame_cropped = frame_resized[:, start_x:end_x]
        else:
            frame_cropped = frame_resized
        image_pil = Image.fromarray(frame_cropped)
        image_tk = ImageTk.PhotoImage(image=image_pil)
        if label == 'original':
            self.original_video_label.configure(image=image_tk)
            # Reference to avoid garbage collection.
            self.original_video_label.image = image_tk 
        elif label == 'processed':
            self.processed_video_label.configure(image=image_tk)
            self.processed_video_label.image = image_tk
        self.window.update_idletasks()
