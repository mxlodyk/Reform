import squat_analysis as sa
import deadlift_analysis as da
import free_weight

def main():
    select_analyser()

def select_analyser():
    # Initialise test data
    exercise = 1
    video_path = "squats/side/demo_barbell_squat_0.mov"

    if exercise == 1:
        free_weight_detector = free_weight.FreeWeight()
        analyser = sa.SquatAnalyser()
        analyser.results.barbell, analyser.results.bar_path = free_weight_detector.detect_barbell(video_path) 
        #analyser.process_video(video_path)
        #analyser.results.print_results()
        print(f"Adequate: {analyser.results.torso_adequate}")
        print(f"Upright {analyser.results.torso_too_upright}")
        print(f"Forward: {analyser.results.torso_too_forward}")
        #print(f"Barbell: {analyser.results.barbell}")
        #print(f"Straight Path: {analyser.results.bar_path}")
    elif exercise == 2:
        free_weight_detector = free_weight.FreeWeight()
        # free_weight_detector.train_model()
        analyser = da.DeadliftAnalyser()
        analyser.results.barbell, analyser.results.bar_path = free_weight_detector.detect_barbell(video_path)
        analyser.process_video(video_path)
        analyser.results.print_results()
    else:
        pass

if __name__ == "__main__":
    main()