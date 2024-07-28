import cv2
import mediapipe as mp
import numpy as np
from helpers import calculate_angle

class SquatAnalyser:

    performing_squat = False
    completed_squat = False
    feet_too_far = False
    feet_too_close = False
    left_toes_too_outward = False
    right_toes_too_outward = False
    left_toes_too_inward = False
    right_toes_too_inward = False
    left_knee_inward = False
    right_knee_inward = False
    torso_too_forward = False
    torso_too_upright = False
    too_shallow = False
    too_deep = False

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
                    self.draw_landmarks(results, image)
                    self.extract_landmarks(landmarks)
                    self.analyse_form(image)
                cv2.imshow("MediaPipe Feed", image)
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    break
        cap.release()
        cv2.destroyAllWindows()

    # Draw landmarks
    def draw_landmarks(self, results, image):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=6),)

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

    # Convert normalised coordinates to pixel coordinates
    def convert_coordinates(self, landmark, image):
        pixel_coordinates = (int(landmark[0] * image.shape[1]), int(landmark[1] * image.shape[0]))
        return pixel_coordinates

    # Analyse form
    def analyse_form(self, image):

        # Analyse feet stance
        if ("left_heel" in self.landmarks and "right_heel" in self.landmarks and "left_shoulder" in self.landmarks
                and "right_shoulder" in self.landmarks):
            left_heel = self.landmarks["left_heel"]
            right_heel = self.landmarks["right_heel"]
            left_shoulder = self.landmarks["left_shoulder"]
            right_shoulder = self.landmarks["right_shoulder"]
            feet_distance = np.sqrt((left_heel[0] - right_heel[0]) ** 2 + (left_heel[1] - right_heel[1]) ** 2)
            shoulder_distance = np.sqrt((left_shoulder[0] - right_shoulder[0]) ** 2 + (left_shoulder[1] -
                                                                                       right_shoulder[1]) ** 2)
            if feet_distance > 1.1 * shoulder_distance:
                self.feet_too_far = True
                # left_heel_pixel = self.convert_coordinates(self.landmarks["left_heel"], image)
                # right_heel_pixel = self.convert_coordinates(self.landmarks["right_heel"], image)
                # left_shoulder_pixel = self.convert_coordinates(self.landmarks["left_shoulder"], image)
                # right_shoulder_pixel = self.convert_coordinates(self.landmarks["right_shoulder"], image)
                # cv2.line(image, left_heel_pixel, left_shoulder_pixel, (0, 0, 255), 1)
                # cv2.line(image, right_heel_pixel, right_shoulder_pixel, (0, 0, 255), 1)
            elif feet_distance < 0.9 * shoulder_distance:
                self.feet_too_close = True
            else:
                pass

        # Check toes
        left_toes_angle = calculate_angle(self.landmarks["left_toes"], self.landmarks["left_ankle"],
                                          self.landmarks["right_ankle"])
        left_toes_pixel = self.convert_coordinates(self.landmarks["left_toes"], image)
        if left_toes_angle > 140:
            self.left_toes_too_outward = True
            cv2.circle(image, left_toes_pixel, 2, (0, 0, 255), 12)
        elif left_toes_angle < 120:
            self.left_toes_too_inward = True
            cv2.circle(image, left_toes_pixel, 2, (0, 0, 255), 12)
        else:
            pass
        right_toes_angle = calculate_angle(self.landmarks["right_toes"], self.landmarks["right_ankle"],
                                           self.landmarks["left_ankle"])
        right_toes_pixel = self.convert_coordinates(self.landmarks["right_toes"], image)
        if right_toes_angle > 140:
            self.right_toes_too_outward = True
            cv2.circle(image, right_toes_pixel, 2, (0, 0, 255), 12)
        elif right_toes_angle < 120:
            self.right_toes_too_inward = True
            cv2.circle(image, right_toes_pixel, 2, (0, 0, 255), 12)
        else:
            pass

        # Determine when squat is completed
        hip_knee_heel_angle = calculate_angle(self.landmarks["left_hip"], self.landmarks["left_knee"], self.landmarks["left_heel"])
        if hip_knee_heel_angle > 120:
            if self.performing_squat:
                self.performing_squat = False
                self.completed_squat = True

        # Determine when squat is being executed
        if hip_knee_heel_angle < 120:
            self.performing_squat = True
            self.completed_squat = False

            # Analyse knees during squat execution
            left_knee_pixel = self.convert_coordinates(self.landmarks["left_knee"], image)
            if self.landmarks["left_knee"] < self.landmarks["left_ankle"]:
                self.left_knee_inward = True
                cv2.circle(image, left_knee_pixel, 2, (0, 0, 255), 12)
            else:
                pass
            if self.landmarks["right_knee"] < self.landmarks["right_ankle"]:
                self.right_knee_inward = True
            else:
                pass

            # Determine values at deepest point in squat
            deepest_squat_angle = float('inf')
            if hip_knee_heel_angle < deepest_squat_angle:
                deepest_squat_angle = hip_knee_heel_angle

                left_hip_y = self.landmarks["left_hip"][1]
                left_knee_y = self.landmarks["left_knee"][1]
                left_hip_pixel = self.convert_coordinates(self.landmarks["left_hip"], image)
                left_knee_pixel = self.convert_coordinates(self.landmarks["left_knee"], image)

                # Analyse squat depth
                if left_hip_y < left_knee_y:
                    self.too_shallow = True
                    cv2.line(image, left_hip_pixel, left_knee_pixel, (0, 165, 255), 6)
                else:
                    pass

                if deepest_squat_angle < 30:
                    self.too_deep = True
                    cv2.line(image, left_hip_pixel, left_knee_pixel, (0, 0, 255), 6)
                else:
                    pass

                # Analyse torso position
                torso_angle = calculate_angle(self.landmarks["left_shoulder"], self.landmarks["left_hip"], self.landmarks["left_knee"])
                shin_angle = calculate_angle(self.landmarks["left_hip"], self.landmarks["left_knee"],
                                             self.landmarks["left_heel"])
                left_shoulder_pixel = self.convert_coordinates(self.landmarks["left_shoulder"], image)
                torso_shin_angle_diff = torso_angle - shin_angle
                if torso_shin_angle_diff > 5:
                    self.torso_too_upright = True
                    cv2.line(image, left_shoulder_pixel, left_hip_pixel, (0, 0, 255), 6)
                elif torso_shin_angle_diff < -5:
                    self.torso_too_forward = False
                    cv2.line(image, left_shoulder_pixel, left_hip_pixel, (0, 0, 255), 6)
                else:
                    pass

    # Print results
    def print_results(self):
        if self.feet_too_far:
            print("Feet too far.")
        elif self.feet_too_close:
            print("Feet too close.")
        else:
            print("Feet are adequate.")
        if self.left_toes_too_outward and self.right_toes_too_outward:
            print("Toes too outward.")
        elif self.left_toes_too_outward and not self.right_toes_too_outward:
            print("Left toes too outward.")
        elif self.right_toes_too_outward and not self.left_toes_too_outward:
            print("Right toes too outward.")
        else:
            print("Toes are adequate.")
        if self.left_knee_inward and self.right_knee_inward:
            print("Knees are inward.")
        elif self.left_knee_inward and not self.right_knee_inward:
            print("Left knee is inward.")
        elif self.right_knee_inward and not self.left_knee_inward:
            print("Right knee is inward.")
        else:
            print("Knees are adequate.")
        if self.too_shallow:
            print("Squat is too shallow.")
        elif self.too_deep:
            print("Squat is too deep.")
        else:
            print("Squat depth is adequate.")
        if self.torso_too_upright:
            print("Torso is too upright.")
        elif self.torso_too_forward:
            print("Torso is leaning too far forward.")
        else:
            print("Torso is adequate.")
