import analysis
import start_gui

video_path = "deadlifts/demo_deadlift_0.mov"

# Get user input
start_window = start_gui.StartGUI()
exercise, video_path = start_window.get_values()

if exercise == "squat":
    analysis1 = analysis.Squat(video_path)
    print(analysis1.results)
elif exercise == "deadlift":
    analysis1 = analysis.Deadlift(video_path)
    print(analysis1.results)
else:
    print("Invalid exercise. Please enter 'squat' or 'deadlift'.")