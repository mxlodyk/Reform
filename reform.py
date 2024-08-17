import squat_analyser as sa
import deadlift_analyser as da
import barbell_detector
#from tkinter import *

def main():

    # window = Tk()
    # window.geometry("500x500")
    # window.title("Reform")
    #
    # # Fix
    # label = Label(window, text="Absolute video path: ", font=('Arial', 18))
    # label.pack()
    #
    # textbox = Text(window, font=('Arial', 16))
    # textbox.pack()
    #
    # button = Button(window, text="Select", font=('Arial', 16))
    # button.pack()

    # Get user input
    # exercise = input("Select exercise:\n"
    #                  "1. Squat\n"
    #                  "2. Deadlift\n"
    #                  "3. Row\n")
    #
    # video_path = input("Enter video path:\n")
    
    select_analyser()
    #window.mainloop()

def select_analyser():
    # Initialise test data
    exercise = 2
    video_path = "deadlifts/demo_deadlift_3.mov"

    if exercise == 1:
        detector = barbell_detector.BarbellDetector()
        analyser = sa.SquatAnalyser()
        detector.process_video(video_path)
        analyser.process_video(video_path)
        analyser.results.print_results()
    elif exercise == 2:
        detector = barbell_detector.BarbellDetector()
        #detector.train_model()
        #analyser = da.DeadliftAnalyser()
        detector.process_video(video_path)
        #analyser.process_video(video_path)
        #analyser.results.print_results()
    else:
        pass

if __name__ == "__main__":
    main()