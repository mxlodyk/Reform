import cv2
import mediapipe as mp
import numpy as np
from helpers import calculate_angle
from helpers import convert_coordinates
import deadlift_results

class DeadliftAnalyser:

    results = deadlift_results.DeadliftResults()

    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.landmarks = {}

    # Process video
    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert video colour formatting to RGB for MediaPipe processing
                image.flags.writeable = False
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # Convert video colour formatting back to BGR for OpenCV drawing
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    self.determine_view(landmarks)
                    self.draw_landmarks(results, image)
                    self.extract_landmarks(landmarks)
                    if self.results.front_view:
                        print("Front View.")
                        #self.analyse_front_view(image)
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

    # Determine if deadlift is recorded from front view or side view
    def determine_view(self, landmarks):
        right_knee_visibility = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility
        left_knee_visibility = landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].visibility
        if right_knee_visibility > 0.8 and left_knee_visibility > 0.8:
            self.results.front_view = True
        elif right_knee_visibility > 0.8 and not left_knee_visibility > 0.8:
            self.results.right_view = True
        elif left_knee_visibility > 0.8 and not right_knee_visibility > 0.8:
            self.results.left_view = True
        else:
            pass

    # Draw landmarks
    def draw_landmarks(self, results, image):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=6),
                                       self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=6, circle_radius=6))

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

    def analyse_side_view(self, image):

        shoulder_hip_knee_angle = calculate_angle(self.landmarks["left_shoulder"], self.landmarks["left_hip"],
                                              self.landmarks["left_knee"])
        cv2.putText(image, str(shoulder_hip_knee_angle),
                    # Convert normalised coordinates to coordinates based on size of video feed
                    tuple(np.multiply(self.landmarks["left_hip"], [1080, 1920]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Start position
        if shoulder_hip_knee_angle > 150 and self.results.performing_deadlift == False:
            self.results.performing_deadlift = False
        # Performing deadlift
        elif shoulder_hip_knee_angle < 150:
            self.results.performing_deadlift = True

            # Determine top position
            if shoulder_hip_knee_angle > self.results.top_position_angle:
                self.results.top_position_angle = shoulder_hip_knee_angle

        if shoulder_hip_knee_angle >= self.results.top_position_angle and self.results.performing_deadlift == True:
            self.results.top_position = True
        else:
            self.results.top_position = False

        # Check if left hip y is lower than left shoulder y at any point in deadlift.
        left_hip_pixel = convert_coordinates(self.landmarks["left_hip"], image)
        if self.landmarks["left_hip"][1] < self.landmarks["left_shoulder"][1]:
            self.results.hips_higher_than_shoulders = True
            cv2.circle(image, left_hip_pixel, 2, (0, 0, 255), 12)

        # Check back at top position
        if self.results.top_position:
            if shoulder_hip_knee_angle > 175:
                self.results.back_overextended = True
                #print("Back OVEREXTENDED at top position")
            else:
                self.results.back_neutral = True
                #self.results.back_overextended[0] = False

    def write_text(self, image):

        if self.results.left_view or self.results.right_view:
            cv2.putText(image, 'Side View', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Hip', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Back', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)

            if self.results.hips_higher_than_shoulders:
                cv2.putText(image, 'Hips Higher than Shoulders', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(image, 'Adequate', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)

            if self.results.back_overextended:
                cv2.putText(image, 'Back Overextended at Top', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
            elif self.results.back_neutral:
                cv2.putText(image, 'Back Neutral at Top', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                pass