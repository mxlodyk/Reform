import analysis
import gui
import threading

video_path = "squats/side/poor_bar_path_2.mov"
output_path = "processed_video.mp4"

# Get user input.
start_window = gui.StartGUI()
start_window.display()
exercise, video_path = start_window.get_values()

if exercise == "squat":
    analysis_window = gui.AnalysisGUI()
    analysis1 = analysis.Squat(video_path)
    threading.Thread(target=analysis1.process_video, args=(analysis_window,), daemon=True).start()
    analysis_window.display(analysis1)
elif exercise == "deadlift":
    analysis1 = analysis.Deadlift(video_path)
else:
    print("Invalid exercise. Please enter 'squat' or 'deadlift'.")