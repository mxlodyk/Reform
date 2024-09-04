import squat
import deadlift
import gui
import threading
import os
from tkinter import messagebox

def main():

    # Get user input.
    launch_window = gui.Launch()
    exercise, video_path = launch_window.get_values()
    analysis_window = gui.Analysis()

    # Check if the video path is valid.
    if not os.path.isfile(video_path):
            messagebox.showerror("Error", f"The video file '{video_path}' does not exist.")

    if exercise == "Squat":
        analysis1 = squat.Squat(video_path)
        analysis1.exercise = "squat"
        analysis_window.analysis = analysis1
        threading.Thread(target=analysis1.process_video, args=(analysis_window,), daemon=True).start()
        analysis_window.display(analysis1)
    elif exercise == "Deadlift":
        analysis1 = deadlift.Deadlift(video_path)
        analysis1.exercise = "deadlift"
        analysis_window.analysis = analysis1
        threading.Thread(target=analysis1.process_video, args=(analysis_window,), daemon=True).start()
        analysis_window.display(analysis1)
    else:
        launch_window.show_selection_error()
        print("Please select an exercise from the drop down menu.")

if __name__ == "__main__":
    main()