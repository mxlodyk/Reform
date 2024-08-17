import cv2
import mediapipe as mp

class VideoHelpers:

    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.landmarks = {}

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                image = cv2.cvtColor(frame,
                                     cv2.COLOR_BGR2RGB)  # Convert video colour formatting to RGB for MediaPipe processing
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image,
                                     cv2.COLOR_RGB2BGR)  # Convert video colour formatting back to BGR for OpenCV drawing
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    self.determine_view(landmarks)
                    self.draw_landmarks(results, image)
                    self.extract_landmarks(landmarks)
                    if self.results.front_view:
                        print("Front View.")
                        # self.analyse_front_view(image)
                    elif self.results.right_view or self.results.left_view:
                        self.analyse_side_view(image)
                    else:
                        pass
                    self.write_text(image)
                cv2.imshow("MediaPipe Feed", image)
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    break
             
        
        cap.release()
        cv2.destroyAllWindows()