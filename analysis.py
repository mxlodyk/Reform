import cv2
import mediapipe as mp
from ultralytics import YOLO

class Analysis:

     # If a weight is detected, the weight type and a set containing all of its coordinates are stored
     weight = {"type": "",
               "coordinates": []
               }
     
     def __init__(self, video_path):
          self.mp_drawing = mp.solutions.drawing_utils
          self.mp_pose = mp.solutions.pose
          self.landmarks = {}
          self.video_path = video_path
     
     # =============
     # Detect weight
     # =============
     def detect_weight(self):
        
        model = YOLO('runs/detect/barbell_detector/weights/best.pt')
        cap = cv2.VideoCapture(self.video_path)
        print("Detecting barbell presence...")
        # Process video
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Detect object
            results = model(frame, verbose=False)
            annotated = results[0].plot()
            cv2.imshow("YOLO Feed", annotated)
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break
            for result in results:
                for detection in result.boxes:
                    confidence = detection.conf.item()
                    # If detection confidence score is greater than 70%
                    if confidence > 0.7:
                         # If 'barbell' class is detected
                         if detection.cls == 0:
                            # Set weight type
                            self.weight["type"] = "barbell"
                            box = detection.xywh[0]
                            x_coordinate = (box[0].item())
                            y_coordinate = (box[1].item())
                            # Append current coordinates
                            self.weight["coordinates"].append((x_coordinate, y_coordinate))
        cap.release()
        cv2.destroyAllWindows()

     # Detect landmarks
     def detect_landmarks(self):
        cap = cv2.VideoCapture(self.video_path)
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                # Convert video colour formatting to RGB for MediaPipe processing
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                # Convert video colour formatting back to BGR for OpenCV drawing
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    self.extract_landmarks(landmarks)
                    self.draw_landmarks(results, image)
                    #self.determine_view(landmarks)
                cv2.imshow("MediaPipe Feed", image)
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    break
        cap.release()
        cv2.destroyAllWindows()

     # Extract x and y coordinates of landmarks and add to landmarks dictionary
     def extract_landmarks(self, landmarks):

        self.landmarks = {"left_hip": [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y],
                          "right_hip": [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y],
                          "left_knee": [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y],
                          "right_knee": [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y],
                          "left_heel": [landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL.value].y],
                          "right_heel": [landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL.value].y],
                          "left_shoulder": [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                          "right_shoulder": [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                          "left_toes": [landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y],
                          "right_toes": [landmarks[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y],
                          "left_ankle": [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y],
                          "right_ankle": [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                        }
        
     # Draw landmarks
     def draw_landmarks(self, results, image):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=6),
                                       self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=6, circle_radius=6))

     
class Squat(Analysis):
     pass

class Deadlift(Analysis):
    pass
     