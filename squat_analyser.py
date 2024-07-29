import cv2
import mediapipe as mp
import numpy as np
from helpers import calculate_angle
from helpers import convert_coordinates
import squat_results

class SquatAnalyser:

    results = squat_results.SquatResults()

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
                    self.analyse_form(image)
                    self.write_text(image)
                cv2.imshow("MediaPipe Feed", image)
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    break
        cap.release()
        cv2.destroyAllWindows()

    # Determine if squat is recorded from front view or side view
    def determine_view(self, landmarks):
        right_ankle_visibility = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].visibility
        left_ankle_visibility = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].visibility
        if right_ankle_visibility > 0.9 and left_ankle_visibility > 0.9:
            self.results.front_view = True
        elif right_ankle_visibility > 0.9 and not left_ankle_visibility > 0.9:
            self.results.right_view = True
        elif left_ankle_visibility > 0.9 and not right_ankle_visibility > 0.9:
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

    # Analyse form
    def analyse_form(self, image):

        if self.results.front_view:
            # Analyse distance between feet
            left_heel = self.landmarks["left_heel"]
            right_heel = self.landmarks["right_heel"]
            left_shoulder = self.landmarks["left_shoulder"]
            right_shoulder = self.landmarks["right_shoulder"]

            feet_distance = np.sqrt((left_heel[0] - right_heel[0]) ** 2 + (left_heel[1] - right_heel[1]) ** 2)
            shoulder_distance = np.sqrt((left_shoulder[0] - right_shoulder[0]) ** 2 + (left_shoulder[1] -
                                                                                       right_shoulder[1]) ** 2)
            left_heel_pixel = convert_coordinates(self.landmarks["left_heel"], image)
            right_heel_pixel = convert_coordinates(self.landmarks["right_heel"], image)
            left_shoulder_pixel = convert_coordinates(self.landmarks["left_shoulder"], image)
            right_shoulder_pixel = convert_coordinates(self.landmarks["right_shoulder"], image)

            if feet_distance > 1.1 * shoulder_distance:
                self.results.feet_too_far = True
                cv2.line(image, left_heel_pixel, left_shoulder_pixel, (0, 0, 255), 2)
                cv2.line(image, right_heel_pixel, right_shoulder_pixel, (0, 0, 255), 2)
                cv2.circle(image, left_heel_pixel, 2, (0, 0, 255), 12)
                cv2.circle(image, right_heel_pixel, 2, (0, 0, 255), 12)
            elif feet_distance < 0.9 * shoulder_distance:
                self.results.feet_too_close = True
                cv2.line(image, left_heel_pixel, left_shoulder_pixel, (0, 0, 255), 2)
                cv2.line(image, right_heel_pixel, right_shoulder_pixel, (0, 0, 255), 2)
                cv2.circle(image, left_heel_pixel, 2, (0, 0, 255), 12)
                cv2.circle(image, right_heel_pixel, 2, (0, 0, 255), 12)
            else:
                self.results.feet_too_close = False
                self.results.feet_too_far = False
                cv2.line(image, left_heel_pixel, left_shoulder_pixel, (0, 255, 0), 2)
                cv2.line(image, right_heel_pixel, right_shoulder_pixel, (0, 255, 0), 2)

            # Analyse positioning of toes
            left_toes_angle = calculate_angle(self.landmarks["left_toes"], self.landmarks["left_ankle"],
                                              self.landmarks["right_ankle"])
            left_toes_pixel = convert_coordinates(self.landmarks["left_toes"], image)
            right_toes_angle = calculate_angle(self.landmarks["right_toes"], self.landmarks["right_ankle"],
                                               self.landmarks["left_ankle"])
            right_toes_pixel = convert_coordinates(self.landmarks["right_toes"], image)
            if left_toes_angle > 140:
                self.results.left_toes_too_outward = True
                self.results.left_toes_too_inward = False
                cv2.circle(image, left_toes_pixel, 2, (0, 0, 255), 12)
            elif left_toes_angle < 120:
                self.results.left_toes_too_inward = True
                self.results.left_toes_too_outward = False
                cv2.circle(image, left_toes_pixel, 2, (0, 0, 255), 12)
            elif right_toes_angle > 140:
                self.results.right_toes_too_outward = True
                self.results.right_toes_too_inward = False
                cv2.circle(image, right_toes_pixel, 2, (0, 0, 255), 12)
            elif right_toes_angle < 120:
                self.results.right_toes_too_inward = True
                self.results.right_toes_too_outward = False
                cv2.circle(image, right_toes_pixel, 2, (0, 0, 255), 12)
            else:
                self.results.left_toes_too_outward = False
                self.results.left_toes_too_inward = False
                self.results.right_toes_too_inward = False
                self.results.right_toes_too_outward = False

            # Analyse knees during squat execution
            left_knee_pixel = convert_coordinates(self.landmarks["left_knee"], image)
            if self.landmarks["left_knee"] < self.landmarks["left_ankle"]:
                self.results.left_knee_inward = True
                cv2.circle(image, left_knee_pixel, 2, (0, 0, 255), 12)
            else:
                self.results.left_knee_inward = False

            if self.landmarks["right_knee"] > self.landmarks["right_ankle"]:
                self.results.right_knee_inward = True
            else:
                self.results.right_knee_inward = False

        # Determine when squat is completed
        hip_knee_heel_angle = calculate_angle(self.landmarks["left_hip"], self.landmarks["left_knee"], self.landmarks["left_heel"])
        cv2.putText(image, str(hip_knee_heel_angle),
                    # Convert normalised coordinates to coordinates based on size of video feed
                    tuple(np.multiply(self.landmarks["left_knee"], [1080, 1920]).astype(int)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Determine when squat is being executed
        if hip_knee_heel_angle < 120:
            self.results.performing_squat = True
            self.results.completed_squat = False

        elif hip_knee_heel_angle > 120:
                self.results.performing_squat = False
                self.results.completed_squat = True

        if self.results.left_view or self.results.right_view:
            # Analyse torso position
            torso_angle = calculate_angle(self.landmarks["left_shoulder"], self.landmarks["left_hip"],
                                          self.landmarks["left_knee"])
            shin_angle = calculate_angle(self.landmarks["left_hip"], self.landmarks["left_knee"],
                                         self.landmarks["left_heel"])
            left_shoulder_pixel = convert_coordinates(self.landmarks["left_shoulder"], image)
            left_hip_pixel = convert_coordinates(self.landmarks["left_hip"], image)
            torso_shin_angle_diff = torso_angle - shin_angle
            if torso_shin_angle_diff > 5:
                self.results.torso_too_upright = True
                self.results.torso_too_forward = False
                cv2.line(image, left_shoulder_pixel, left_hip_pixel, (0, 0, 255), 6)
            elif torso_shin_angle_diff < -5:
                self.results.torso_too_forward = True
                self.results.torso_too_upright = False
                cv2.line(image, left_shoulder_pixel, left_hip_pixel, (0, 0, 255), 6)
            else:
                self.results.torso_too_upright = False
                self.results.torso_too_forward = False
                cv2.line(image, left_shoulder_pixel, left_hip_pixel, (0, 255, 0), 6)

            # Determine values at deepest point in squat
            left_knee_pixel = convert_coordinates(self.landmarks["left_knee"], image)
            left_hip_pixel = convert_coordinates(self.landmarks["left_hip"], image)

            if hip_knee_heel_angle < self.results.deepest_squat_angle:
                self.results.deepest_squat_angle = hip_knee_heel_angle
                self.results.deepest_squat_left_hip_y = self.landmarks["left_hip"][1]
                self.results.deepest_squat_left_knee_y = self.landmarks["left_knee"][1]

            # Analyse squat depth
            if self.results.deepest_squat_left_hip_y < self.results.deepest_squat_left_knee_y:
                self.results.too_shallow = True
                self.results.too_deep = False
                cv2.line(image, left_hip_pixel, left_knee_pixel, (0, 165, 255), 6)
            elif self.results.deepest_squat_angle < 30:
                self.results.too_deep = True
                self.results.too_shallow = False
                cv2.line(image, left_hip_pixel, left_knee_pixel, (0, 0, 255), 6)
            else:
                self.results.too_deep = False
                self.results.too_shallow = False
                cv2.line(image, left_hip_pixel, left_knee_pixel, (0, 255, 0), 6)

        print(self.results.deepest_squat_angle)



    # Write text to video
    def write_text(self, image):

        if self.results.left_view or self.results.right_view:
            cv2.putText(image, 'Side View', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Torso', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Depth', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)

            if self.results.torso_too_upright:
                cv2.putText(image, 'Too Upright', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
            elif self.results.torso_too_forward:
                cv2.putText(image, 'Too Forward', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(image, 'Adequate', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,
                            cv2.LINE_AA)
            if self.results.too_shallow:
                cv2.putText(image, 'Too Shallow', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2, cv2.LINE_AA)
            elif self.results.too_deep:
                cv2.putText(image, 'Too Deep', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            else:
                cv2.putText(image, 'Adequate', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,
                            cv2.LINE_AA)

        elif self.results.front_view:
            cv2.putText(image, 'Front View', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Feet', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Knees', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, 'Toes', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2, cv2.LINE_AA)

            if self.results.feet_too_far:
                cv2.putText(image, 'Too Far Apart', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.feet_too_close:
                cv2.putText(image, 'Too Close Together', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            else:
                cv2.putText(image, 'Adequate', (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,
                            cv2.LINE_AA)

            if self.results.left_knee_inward and self.results.right_knee_inward:
                cv2.putText(image, 'Both Knees Inward', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.left_knee_inward and not self.results.right_knee_inward:
                cv2.putText(image, 'Left Knee Inward', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.right_knee_inward and not self.results.left_knee_inward:
                cv2.putText(image, 'Right Knee Inward', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif not self.results.right_knee_inward and not self.results.left_knee_inward:
                cv2.putText(image, 'Adequate', (150, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,
                            cv2.LINE_AA)

            if self.results.left_toes_too_outward and self.results.right_toes_too_outward:
                cv2.putText(image, 'Both Toes Too Outward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.left_toes_too_outward and not self.results.right_toes_too_outward:
                cv2.putText(image, 'Left Toes Too Outward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.right_toes_too_outward and not self.results.left_toes_too_outward:
                cv2.putText(image, 'Right Toes Too Outward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.left_toes_too_inward and self.results.right_toes_too_inward:
                cv2.putText(image, 'Both Toes Too Inward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.left_toes_too_inward and not self.results.right_toes_too_inward:
                cv2.putText(image, 'Left Toes Too Inward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            elif self.results.right_toes_too_inward and not self.results.left_toes_too_inward:
                cv2.putText(image, 'Right Toes Too Inward', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2,
                            cv2.LINE_AA)
            else:
                cv2.putText(image, 'Adequate', (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,
                            cv2.LINE_AA)
