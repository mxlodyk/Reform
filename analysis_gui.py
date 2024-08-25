from pathlib import Path

from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage


OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/melodyflavel/Projects/Python/Reform/assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()

window.geometry("1000x500")
window.configure(bg = "#F3F3F3")


canvas = Canvas(
    window,
    bg = "#F3F3F3",
    height = 500,
    width = 1000,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_rectangle(
    651.0,
    44.0,
    959.0,
    456.0,
    fill="#E0E0E0",
    outline="")

canvas.create_rectangle(
    679.0,
    75.0,
    689.0,
    85.0,
    fill="#C10000",
    outline="")

canvas.create_text(
    713.0,
    281.0,
    anchor="nw",
    text="Some description of what the results mean...",
    fill="#5C5C5C",
    font=("ArialMT", 10 * -1)
)

canvas.create_text(
    711.0,
    260.0,
    anchor="nw",
    text="The barbell path is straight.",
    fill="#000000",
    font=("ArialMT", 12 * -1)
)

canvas.create_text(
    711.0,
    237.0,
    anchor="nw",
    text="Barbell Path",
    fill="#000000",
    font=("ArialMT", 16 * -1)
)

canvas.create_text(
    713.0,
    199.0,
    anchor="nw",
    text="Some description of what the results mean...",
    fill="#5C5C5C",
    font=("ArialMT", 10 * -1)
)

canvas.create_text(
    713.0,
    178.0,
    anchor="nw",
    text="The squat is not deep enough.",
    fill="#000000",
    font=("ArialMT", 12 * -1)
)

canvas.create_text(
    711.0,
    155.0,
    anchor="nw",
    text="Depth",
    fill="#000000",
    font=("ArialMT", 16 * -1)
)

canvas.create_text(
    711.0,
    94.0,
    anchor="nw",
    text="The torso is leaning too far forward.",
    fill="#000000",
    font=("ArialMT", 12 * -1)
)

canvas.create_text(
    711.0,
    71.0,
    anchor="nw",
    text="Torso",
    fill="#000000",
    font=("Arial BoldMT", 16 * -1)
)

canvas.create_text(
    711.0,
    115.0,
    anchor="nw",
    text="Some description of what the results mean...",
    fill="#5C5C5C",
    font=("ArialMT", 10 * -1)
)

canvas.create_text(
    770.0,
    18.0,
    anchor="nw",
    text="Analysis",
    fill="#000000",
    font=("Arial BoldMT", 18 * -1)
)

canvas.create_rectangle(
    0.0,
    0.0,
    611.0,
    500.0,
    fill="#A3A3A3",
    outline="")

canvas.create_rectangle(
    679.0,
    241.0,
    689.0,
    251.0,
    fill="#005F19",
    outline="")

canvas.create_rectangle(
    679.0,
    159.0,
    689.0,
    169.0,
    fill="#D68400",
    outline="")
window.resizable(False, False)
window.mainloop()
