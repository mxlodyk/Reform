from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label, messagebox
from PIL import Image, ImageTk
import cv2


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/melodyflavel/Projects/Python/Reform/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class StartGUI:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("400x250")
        self.window.configure(bg = "#F3F3F3")
        self.canvas = Canvas(
            self.window,
            bg = "#F3F3F3",
            height = 250,
            width = 400,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

    def display(self):
        self.canvas.place(x = 0, y = 0)
        self.canvas.create_text(
            35.0,
            24.0,
            anchor="nw",
            text="Exercise",
            fill="#000000",
            font=("ArialMT", 18 * -1)
        )

        self.canvas.create_text(
            35.0,
            104.0,
            anchor="nw",
            text="Video Path",
            fill="#000000",
            font=("ArialMT", 18 * -1)
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(
            198.0,
            70.0,
            image=entry_image_1
        )
        self.entry_1 = Entry(
            bd=0,
            bg="#E6E6E6",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_1.place(
            x=45.0,
            y=54.0,
            width=306.0,
            height=30.0
        )

        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        entry_bg_2 = self.canvas.create_image(
            198.0,
            151.0,
            image=entry_image_2
        )
        self.entry_2 = Entry(
            bd=0,
            bg="#E6E6E6",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_2.place(
            x=45.0,
            y=135.0,
            width=306.0,
            height=30.0
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.get_entry_text,
            relief="flat"
        )
        button_1.place(
            x=86.0,
            y=191.0,
            width=229.0,
            height=39.0
        )
        self.window.resizable(False, False)
        self.window.mainloop()

    def get_entry_text(self):
        self.exercise = self.entry_1.get()
        self.video_path = self.entry_2.get()
        self.window.destroy()
    
    def get_values(self):
        return self.exercise, self.video_path
    
class AnalysisGUI:

    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x500")
        self.window.configure(bg = "#F3F3F3")
        self.canvas = Canvas(
            self.window,
            bg = "#F3F3F3",
            height = 500,
            width = 1000,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.images = {
            "cross": relative_to_assets("cross.png"),
            "exclamation_mark": relative_to_assets("exclamation_mark.png"),
            "check_mark": relative_to_assets("check_mark.png")
        }

        # Label to display the original video.
        self.original_video_label = Label(self.window)
        self.original_video_label.place(x=0, y=0)

        # Label to display the annotated video.
        self.processed_video_label = Label(self.window)
        self.processed_video_label.place(x=(959 - 651), y=0)

        self.window.resizable(False, False)

    def update_analysis_text(self, analysis):
        # Clear previous text.
        self.canvas.delete("analysis_text")

        # Update torso analysis text.
        torso_text = "Torso position is adequate."
        if analysis.results.get("torso", {}).get("current", 0) == "upright":
            torso_text = "The torso is too upright."
        elif analysis.results.get("torso", {}).get("current", 0) == "forward":
            torso_text = "The torso is leaning too far forward."

        # Update depth analysis text.
        depth_text = "The squat depth is adequate."
        if analysis.results.get("depth", {}).get("current", 0) == "shallow":
            depth_text = "The squat is not deep enough."
        elif analysis.results.get("depth", {}).get("current", 0) == "deep":
            depth_text = "The squat is too deep."

        if analysis.weight["type"] == "barbell":
            # Update barbell path analysis text.
            barbell_text = "The barbell path is straight."
            if analysis.results.get("barbell", {}).get("straight", False) == False:
                barbell_text = "The barbell path is not straight."

        # Display the updated text.
        self.canvas.create_text(
            713.0,
            178.0,
            anchor="nw",
            text=depth_text,
            fill="#000000",
            font=("ArialMT", 12 * -1),
            tags="analysis_text"
        )

        self.canvas.create_text(
            711.0,
            155.0,
            anchor="nw",
            text="Depth",
            fill="#000000",
            font=("ArialMT", 16 * -1),
            tags="analysis_text"
        )

        self.canvas.create_text(
            711.0,
            94.0,
            anchor="nw",
            text=torso_text,
            fill="#000000",
            font=("ArialMT", 12 * -1),
            tags="analysis_text"
        )

        self.canvas.create_text(
            711.0,
            71.0,
            anchor="nw",
            text="Torso",
            fill="#000000",
            font=("Arial BoldMT", 16 * -1),
            tags="analysis_text"
        )

        if analysis.weight["type"] == "barbell":
            self.canvas.create_text(
                711.0,
                237.0,
                anchor="nw",
                text="Barbell Path",
                fill="#000000",
                font=("ArialMT", 16 * -1),
                tags="analysis_text"
            )

        if analysis.weight["type"] == "barbell":
            self.canvas.create_text(
                711.0,
                260.0,
                anchor="nw",
                text=barbell_text,
                fill="#000000",
                font=("ArialMT", 12 * -1),
                tags="analysis_text"
            )
        # Ensure the canvas is updated.
        self.window.update_idletasks()
        self.update_result_image(analysis)

    def update_result_image(self, analysis):
        # Positions for the images next to each analysis criterion.
        positions = {
            "torso": (684.0, 80.0),
            "depth": (684.0, 164.0),
            "barbell": (684.0, 245.0)
        }
        # Determine the image to display based on the results.
        def determine_image(result):
            if result == "upright" or result == "forward" or result == "deep" or not analysis.results.get("barbell", {}).get("straight", True):
                return self.images["cross"]
            elif result == "shallow":
                return self.images["exclamation_mark"]
            else:
                return self.images["check_mark"]

        # List of all elements to update.
        elements = ["torso", "depth"]
        if analysis.weight["type"] == "barbell":
            elements.append("barbell")

        # Remove previous images.
        self.canvas.delete("result_image")

        # Update images based on results.
        for element in elements:
            if element == "torso":
                current_result = analysis.results.get("torso", {}).get("current", "")
            elif element == "depth":
                current_result = analysis.results.get("depth", {}).get("current", "")
            else: 
                current_result = "straight" if analysis.results.get("barbell", {}).get("straight", True) else "not_straight"

            # Get the appropriate image for the result.
            image_path = determine_image(current_result)
            image = PhotoImage(file=image_path)
            
            # Place the image in the corresponding position with a unique tag.
            self.canvas.create_image(
                positions[element],
                image=image,
                tags=f"{element}_image"
            )
            
            # Reference to avoid garbage collection.
            setattr(self, f"{element}_image", image)

    def display(self, analysis):
        self.canvas.place(x = 0, y = 0)
        self.canvas.create_rectangle(
            651.0,
            44.0,
            959.0,
            456.0,
            fill="#E0E0E0",
            outline="")

        self.canvas.create_rectangle(
            0.0,
            0.0,
            611.0,
            500.0,
            fill="#A3A3A3",
            outline="")

        self.window.resizable(False, False)
        self.window.mainloop()

    def update_video_frame(self, frame, label):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width = frame_rgb.shape[:2]
        max_height = 500
        max_width = 959 - 651
        scale = max_height / height
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame_resized = cv2.resize(frame_rgb, (new_width, new_height))
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
