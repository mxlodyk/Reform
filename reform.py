import squat_analyser as sa

def main():

    # Get user input
    # exercise = input("Select exercise:\n"
    #                  "1. Squat\n"
    #                  "2. Deadlift\n"
    #                  "3. Row\n")
    #
    # video_path = input("Enter video path:\n")

    # Initialise test data
    exercise = 1
    video_path = "/Users/melodyflavel/Desktop/Squats/KneesInward.MOV"

    if exercise == 1:
        analyser = sa.SquatAnalyser()
        analyser.process_video(video_path)
        analyser.results.print_results()
    else:
        pass

if __name__ == "__main__":
    main()
