import analysis
import gui
import threading
import os
from tkinter import messagebox

def main():

    # deadlifts/side/demo_deadlift_0.mov
    # deadlifts/side/hips_higher_than_shoulders_0.mov
    # deadlifts/side/back_overextended_0.mov
    # deadlifts/side/back_overflexed_0.mov
    # deadlifts/front/adequate_front_0.mov
    # deadlifts/front/feet_far_0.mov
    # deadlifts/front/feet_close_0.mov

    # Get user input.
    launch_window = gui.Launch()
    exercise, video_path = launch_window.get_values()
    analysis_window = gui.Analysis()

    # Check if the video path is valid.
    if not os.path.isfile(video_path):
            messagebox.showerror("Error", f"The video file '{video_path}' does not exist.")

    if exercise == "Squat":
        analysis1 = analysis.Squat(video_path)
        analysis1.exercise = "squat"
        analysis_window.analysis = analysis1
        threading.Thread(target=analysis1.process_video, args=(analysis_window,), daemon=True).start()
        analysis_window.display(analysis1)
    elif exercise == "Deadlift":
        analysis1 = analysis.Deadlift(video_path)
        analysis1.exercise = "deadlift"
        analysis_window.analysis = analysis1
        threading.Thread(target=analysis1.process_video, args=(analysis_window,), daemon=True).start()
        analysis_window.display(analysis1)
    else:
        launch_window.show_selection_error()
        print("Please select an exercise from the drop down menu.")

if __name__ == "__main__":
    main()