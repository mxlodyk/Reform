import numpy as np
import cv2
import mediapipe as mp
from ultralytics import YOLO
from helpers import calculate_angle
from helpers import convert_coordinates

class Analysis:
     
     colours = {
               "red": (0, 0, 255),
               "green": (0, 255, 0),
               "orange": (0, 165, 255)
               }
     
     def __init__(self, video_path):
          self.mp_drawing = mp.solutions.drawing_utils
          self.mp_pose = mp.solutions.pose
          self.video_path = video_path

          self.view = ""
          self.landmarks = {}
          self.results = {}
          self.angles = {}
          self.pixels = {}
          # If a weight is detected, the weight type and a set of all of its coordinates are stored.
          self.exercise = ""
          self.weight = {"type": "",
               "coordinates": []
               }
          
          self.is_playing = False
     
     def process_video(self, gui):
          # Handle race conditions when the 'replay' button is clicked while the video is already
          # playing.
          if self.is_playing:
            print("Video is already playing. Stopping current playback...")
            # Do not start a new thread if the video is already playing.
            return
          self.is_playing = True

          model = YOLO('runs/detect/barbell_detector/weights/best.pt')
          cap = cv2.VideoCapture(self.video_path)

          with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
               frame_count = 0
               while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                         print(f"Video ended or failed to load at frame {frame_count}")
                         break
                    frame_count += 1
                    # Keep the analysis window updated with the original video frame for playback.
                    gui.update_video_frame(frame, label='original')

                    # Detect the presence of a weight.
                    results = model(frame, verbose=False)
                    annotated_frame = results[0].plot()

                    for result in results:
                         for detection in result.boxes:
                              confidence = detection.conf.item()
                              # If detection confidence > 70% and class is 'barbell'.
                              if confidence > 0.7 and detection.cls == 0:
                                   self.weight["type"] = "barbell"
                                   box = detection.xywh[0]
                                   x_coordinate = box[0].item()
                                   y_coordinate = box[1].item()
                                   self.weight["coordinates"].append((x_coordinate, y_coordinate))

                    # Detect landmarks.
                    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image_rgb.flags.writeable = False
                    landmarks_results = pose.process(image_rgb)
                    image_rgb.flags.writeable = True
                    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                    if landmarks_results.pose_landmarks:
                         landmarks = landmarks_results.pose_landmarks.landmark
                         # Perform calculations and analyses for each frame.
                         self.extract_landmarks(landmarks)
                         self.draw_landmarks(landmarks_results, image_bgr)
                         self.get_landmark_pixels(image_bgr)
                         self.calculate_angles()
                         self.calculate_distances()
                         self.calculate_coordinates()
                         self.determine_view()
                         self.initialise_results()
                         if self.weight["type"] == "barbell":
                              self.analyse_bar_path()
                         if self.view == "left" or self.view == "right":
                              self.analyse_side_view(image_bgr)
                         elif self.view == "front":
                              self.analyse_front_view(image_bgr)
                         else:
                              print("View error.")

                    # Update the text in the analysis window depending on the results.
                    gui.update_analysis_text()
                    
                    # Combine the annotations from MediaPipe and YOLO in one frame.
                    combined_frame = cv2.addWeighted(annotated_frame, 0.6, image_bgr, 0.8, 0)
                    # Keep the analysis window updated with the annotated frame for playback.
                    gui.update_video_frame(combined_frame, label='processed')

                    if cv2.waitKey(10) & 0xFF == ord("q"):
                         break

          cap.release()
          cv2.destroyAllWindows()
          self.is_playing = False

     # Extract x and y coordinates of each landmark and add to landmarks dictionary.
     def extract_landmarks(self, landmarks):

        self.landmarks = {"left_hip": [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y],
                          "right_hip": [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y],
                          "left_knee": [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].visibility],
                          "right_knee": [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].visibility],
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
        
     # Draw landmarks and connections on playback video.
     def draw_landmarks(self, results, image):
        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                       self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=6),
                                       self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=8, circle_radius=6))

     # Determine the view that the exercise is being recorded from. The analyses performed on the
     # exercise is dependant on the view. The same analyses cannot be accurately performed on both 
     # views because of limitations in the Pose solution, such as its inability to accurately 
     # measure the distance between the feet when the video is recorded from the side, or 
     # difficulty in detecting certain landmarks when key body parts are occluded in the side view.
     def determine_view(self):
          right_knee_visibility = self.landmarks["right_knee"][2]
          left_knee_visibility = self.landmarks["left_knee"][2]
          confidence = 0 

          if right_knee_visibility >= 0.7 and left_knee_visibility >= 0.7:
              self.view = "front"
              confidence = min(right_knee_visibility, left_knee_visibility)
          elif right_knee_visibility >= 0.7 and not left_knee_visibility >= 0.7:
              self.view = "right"
              confidence = right_knee_visibility / (right_knee_visibility + left_knee_visibility) if (right_knee_visibility + left_knee_visibility) != 0 else 0
          elif left_knee_visibility >= 0.7 and not right_knee_visibility >= 0.7:
              self.view = "left"
              confidence = left_knee_visibility / (left_knee_visibility + right_knee_visibility) if (left_knee_visibility + right_knee_visibility) != 0 else 0
          else:
              print("Error determining the view of the exercise. Please ensure the video adheres to criteria.")

          print(f"View detected: {self.view} with confidence: {confidence:.2f}")

     def analyse_bar_path(self):
          min_x = min(coord[0] for coord in self.weight["coordinates"])
          max_x = max(coord[0] for coord in self.weight["coordinates"])
          if abs(min_x - max_x) > 50:
            return False
          return True
     
     def draw_circle(self, image, pixel, colour, radius=2, size=20):
          cv2.circle(image, pixel, radius, self.colours[colour], size)
     
     def draw_line(self, image, start, end, colour, thickness=8):
         cv2.line(image, start, end, self.colours[colour], thickness)
     
     def draw_dashed_line(self, image, start_point, end_point, colour, thickness=6, dash_length=15, gap_length=15):
        distance = np.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)

        num_dashes = int(distance / (dash_length + gap_length))

        for i in range(num_dashes):
            start = (
                int(start_point[0] + (end_point[0] - start_point[0]) * i / num_dashes),
                int(start_point[1] + (end_point[1] - start_point[1]) * i / num_dashes)
            )
            end = (
                int(start_point[0] + (end_point[0] - start_point[0]) * (i + 0.5) / num_dashes),
                int(start_point[1] + (end_point[1] - start_point[1]) * (i + 0.5) / num_dashes)
            )

            overlay = image.copy()
            opacity = 0.6
            cv2.line(overlay, start, end, self.colours[colour], thickness)
            cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0, image)

     def draw_cross(self, image, pixel, colour, thickness=6, size=15):
          cv2.line(image, (int(pixel[0] - size), int(pixel[1] - size)), (int(pixel[0] + size), 
                                                                         int(pixel[1] + size)), 
                                                                         self.colours[colour], 2)
          cv2.line(image, (int(pixel[0] - size), int(pixel[1] + size)), (int(pixel[0] + size), 
                                                                         int(pixel[1] - size)), 
                                                                         self.colours[colour], 2)
     
     def initialise_results():
         # Placeholder to be overridden by subclasses.
         pass

     def get_landmark_pixels(self):
         # Placeholder to be overridden by subclasses.
         pass

     def calculate_angles(self):
        # Placeholder to be overridden by subclasses.
        pass 

     def calculate_distances(self):
        # Placeholder to be overridden by subclasses.
        pass 

     def calculate_coordinates(self):
         # Placeholder to be overridden by subclasses.
         pass
     
     def analyse_side_view(self):
         # Placeholder to be overridden by subclasses.
         pass

class Deadlift(Analysis):
     def __init__(self, video_path):
          super().__init__(video_path)

     def initialise_results(self):
          if self.view == "left" or self.view == "right":
               if "back" not in self.results:
                    self.results = {
                         "hips": {
                              "current": "",
                              "high": 0,
                              "adequate": 0,
                         },
                         "back": {
                              "current": "",
                              "overextended": False,
                              "adequate": False,
                              "overflexed": False
                         }
                    } 
          if self.view == "front":
               if "feet" not in self.results:
                    self.results = {
                         "feet": {
                              "current": "",
                              "far": False,
                              "adequate": False,
                              "close": False
                         },
                         "right_toes": {
                              "current": "",
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         },
                         "left_toes": {
                              "current": "",
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         }
                    }

     def get_landmark_pixels(self, image):
         self.pixels = {"left_hip":
                    convert_coordinates(self.landmarks["left_hip"], image),
                    "right_hip":
                    convert_coordinates(self.landmarks["right_hip"], image),
                    "left_shoulder":
                    convert_coordinates(self.landmarks["left_shoulder"], image),
                    "right_shoulder":
                    convert_coordinates(self.landmarks["right_shoulder"], image),
                    "left_heel":
                    convert_coordinates(self.landmarks["left_heel"], image),
                    "right_heel":
                    convert_coordinates(self.landmarks["right_heel"], image),
                    "left_toes":
                    convert_coordinates(self.landmarks["left_toes"], image),
                    "right_toes":
                    convert_coordinates(self.landmarks["right_toes"], image)
         }

         if "left_heel" in self.pixels:
             self.pixels["left_heel_target"] = [self.pixels["left_shoulder"][0], self.pixels["left_heel"][1]]
             self.pixels["right_heel_target"] = [self.pixels["right_shoulder"][0], self.pixels["right_heel"][1]]

     def calculate_angles(self):
          self.angles["shoulder_hip_knee_angle"] = calculate_angle(self.landmarks["left_shoulder"], 
                                                            self.landmarks["left_hip"],
                                                            self.landmarks["left_knee"]
          )
          self.angles["left_toes_ankles_angle"] = calculate_angle(self.landmarks["left_toes"],
                                                            self.landmarks["left_ankle"],
                                                            self.landmarks["right_ankle"]
          )
          self.angles["right_toes_ankles_angle"] = calculate_angle(self.landmarks["right_toes"],
                                                            self.landmarks["right_ankle"],
                                                            self.landmarks["left_ankle"]
          )
          # Maintain 'largest_shoulder_hip_knee_angle'.
          if "largest_shoulder_hip_knee_angle" not in self.angles:
            self.angles["largest_shoulder_hip_knee_angle"] = self.angles["shoulder_hip_knee_angle"]
          else:
               self.angles["largest_shoulder_hip_knee_angle"] = max(
               self.angles["largest_shoulder_hip_knee_angle"], 
               self.angles["shoulder_hip_knee_angle"]
            )
     
     # Calculate specific coordinates required for analysis.
     def calculate_distances(self):
         self.distances = {
                    "feet_distance": np.sqrt((self.landmarks["left_heel"][0] - self.landmarks["right_heel"][0]) ** 2 +
                                        (self.landmarks["left_heel"][1] - self.landmarks["right_heel"][1]) ** 2),
                    "shoulder_distance": np.sqrt((self.landmarks["left_shoulder"][0] - self.landmarks["right_shoulder"][0]) ** 2 +
                                            (self.landmarks["left_shoulder"][1] - self.landmarks["right_shoulder"][1]) ** 2)
                    }
     
     def determine_phase(self):
          if self.view == "left" or self.view == "right":
               if self.angles["shoulder_hip_knee_angle"] >= 150:
                    return "standing"
               elif self.angles["shoulder_hip_knee_angle"] < 150:
                    return "deadlifting"
          if self.view == "front":
              pass
               
     def analyse_side_view(self, image):
          # cv2.putText(image, str(self.angles["shoulder_hip_knee_angle"]),
          #           # Convert normalised coordinates to coordinates based on size of video feed
          #           tuple(np.multiply(self.landmarks["left_hip"], [1080, 1920]).astype(int)),
          #           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
          
          def analyse_hip():
               if self.landmarks["left_hip"][1] < self.landmarks["left_shoulder"][1] or self.landmarks["right_hip"][1] < self.landmarks["right_shoulder"][1]:
                    self.results["hips"]["high"] = True
                    self.results["hips"]["current"] = "high"
                    self.draw_circle(image, self.pixels["left_hip"], "red")
                    self.draw_circle(image, self.pixels["right_hip"], "red")

          def analyse_back():
               if self.results["back"]["overextended"]:
                    self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "red")
                    return

               current_phase = self.determine_phase()
               if current_phase == "standing":
                    if self.angles["shoulder_hip_knee_angle"] >= 175:
                         self.results["back"]["overextended"] = True
                         self.results["back"]["current"] = "overextended"
                         self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "red")
                    if self.angles["largest_shoulder_hip_knee_angle"] < 165:
                         self.results["back"]["overflexed"] = True
                         self.results["back"]["current"] = "overflexed"
                         self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "red")
                    else:
                         self.results["back"]["adequate"] = True
                         self.results["back"]["current"] = "adequate"
                         self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "green")

          analyse_hip()
          analyse_back()

     def analyse_front_view(self, image):
         
          # Analyse the feet stance based on the distance between the feet and the distance between
         # the shoulders. If the feet are shoulder-width apart or within a 0.2 tolerance, the feet are
         # adequately stanced for a conventional squat.
          def analyse_feet_stance():
               # Feet are too far apart for a conventional squat.
               if self.distances["feet_distance"] > 1.1 * self.distances["shoulder_distance"]:
                    self.results["feet"]["far"] = True
                    self.results["feet"]["current"] = "far"
                    self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "red")
                    self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "red")
                    self.draw_cross(image, self.pixels["left_heel_target"], "red")
                    self.draw_cross(image, self.pixels["right_heel_target"], "red")
                    self.draw_circle(image, self.pixels["left_heel"], "red")
                    self.draw_circle(image, self.pixels["right_heel"], "red")
               # Feet are too close together for a conventional squat.
               elif self.distances["feet_distance"] < 0.7 * self.distances["shoulder_distance"]:
                   self.results["feet"]["close"] = True
                   self.results["feet"]["current"] = "close"
                   self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "red")
                   self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "red")
                   self.draw_cross(image, self.pixels["left_heel_target"], "red")
                   self.draw_cross(image, self.pixels["right_heel_target"], "red")
                   self.draw_circle(image, self.pixels["left_heel"], "red")
                   self.draw_circle(image, self.pixels["right_heel"], "red")
               # Feet are adequately stanced for a conventional squat.
               else:
                   self.results["feet"]["adequate"] = True
                   self.results["feet"]["current"] = "adequate"
                   self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "green")
                   self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "green")
                   self.draw_cross(image, self.pixels["left_heel_target"], "green")
                   self.draw_cross(image, self.pixels["right_heel_target"], "green")
                   self.draw_circle(image, self.pixels["left_heel"], "green")
                   self.draw_circle(image, self.pixels["right_heel"], "green")

          def analyse_toes():
               if self.angles["left_toes_ankles_angle"] > 140:
                 self.results["left_toes"]["outward"] == True
                 self.results["left_toes"]["current"] = "outward"
                 self.draw_circle(image, self.pixels["left_toes"], "red")
               elif self.angles["left_toes_ankles_angle"] < 110:
                    self.results["left_toes"]["inward"] == True
                    self.results["left_toes"]["current"] = "inward"
                    self.draw_circle(image, self.pixels["left_toes"], "red")
               else:
                   self.results["left_toes"]["adequate"] == True
                   self.results["left_toes"]["current"] = "adequate"
                   self.draw_circle(image, self.pixels["left_toes"], "green")

               if self.angles["right_toes_ankles_angle"] > 140:
                 self.results["right_toes"]["outward"] == True
                 self.results["right_toes"]["current"] = "outward"
                 self.draw_circle(image, self.pixels["right_toes"], "red")
               elif self.angles["right_toes_ankles_angle"] < 110:
                    self.results["right_toes"]["inward"] == True
                    self.results["right_toes"]["current"] = "inward"
                    self.draw_circle(image, self.pixels["right_toes"], "red")
               else:
                   self.results["right_toes"]["adequate"] == True
                   self.results["right_toes"]["current"] = "adequate"
                   self.draw_circle(image, self.pixels["right_toes"], "green")

          analyse_feet_stance()
          analyse_toes()