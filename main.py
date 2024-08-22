import analysis

video_path = "squats/side/demo_barbell_squat_0.mov"

analysis1 = analysis.Analysis(video_path)
analysis1.detect_weight()
analysis1.detect_landmarks()
print(analysis1.weight["coordinates"])