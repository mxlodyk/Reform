from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/melodyflavel/Projects/Python/Reform/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class StartGUI:
    window = Tk()

    window.geometry("400x250")
    window.configure(bg = "#F3F3F3")

    canvas = Canvas(
        window,
        bg = "#F3F3F3",
        height = 250,
        width = 400,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    def __init__(self):
        self.display()

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
