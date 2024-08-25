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
          self.weight = {"type": "",
               "coordinates": []
               }
     
     def process_video(self, gui):
          model = YOLO('runs/detect/barbell_detector/weights/best.pt')
          cap = cv2.VideoCapture(self.video_path)

          with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
               while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                         break
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
                         if self.view == "left":
                              self.analyse_side_view(image_bgr)
                         elif self.view == "front":
                              self.analyse_front_view(image_bgr)
                         else:
                             print("View error.")

                    # Update the text in the analysis window depending on the results.
                    gui.update_analysis_text(self)
                    
                    # Combine the annotations from MediaPipe and YOLO in one frame.
                    combined_frame = cv2.addWeighted(annotated_frame, 0.3, image_bgr, 0.7, 0)
                    # Keep the analysis window updated with the annotated frame for playback.
                    gui.update_video_frame(combined_frame, label='processed')

                    if cv2.waitKey(10) & 0xFF == ord("q"):
                         break

          cap.release()
          cv2.destroyAllWindows()

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
     # exercise is dependant on the view. The same analyses cannot be accurately 
     # performed on both views because of limitations in the Pose solution, such as its inability to 
     # accurately measure the distance between the feet when the video is recorded from the side, or 
     # difficulty in detecting certain landmarks when key body parts are occluded in the side view.
     def determine_view(self):
          right_knee_visibility = self.landmarks["right_knee"][2]
          left_knee_visibility = self.landmarks["left_knee"][2]
          if right_knee_visibility > 0.8 and left_knee_visibility > 0.8:
              self.view = "front"
          elif right_knee_visibility > 0.8 and not left_knee_visibility > 0.8:
              self.view = "right"
          elif left_knee_visibility > 0.8 and not right_knee_visibility > 0.8:
              self.view = "left"
          else:
              print("Error determining view.")

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
     

class Squat(Analysis):

     def __init__(self, video_path):
          super().__init__(video_path)

     # Initialise a dictionary containing the results of the analysis. The contents are dependant on
     # whether the squat is being analysed from the front view or side view.
     def initialise_results(self):
          if self.view == "left" or self.view == "right":
               if "torso" not in self.results:
                    self.results = {
                         "torso": {
                              # Counters are used to store the total number of frames that
                              # the torso is in each criterion. This is used to determine the
                              # overall result of the torso position, rather than only the last
                              # recorded position of the torso. The 'current' key is used to get the
                              # current state of the torso for displaying the live feedback in the
                              # analysis GUI.
                              "current": "",
                              "upright": 0,
                              "adequate": 0,
                              "forward": 0
                         },
                         "depth": {
                             "current": "",
                              "shallow": False,
                              "adequate": False,
                              "deep": False
                         }
                    }
               if self.weight["type"] == "barbell" and "barbell" not in self.results:
                    self.results["barbell"] = {
                         "straight": True,
                    }
          if self.view == "front":
               if "feet" not in self.results:
                    self.results = {
                         "feet": {
                              "far": False,
                              "adequate": False,
                              "close": False
                         },
                         "right_toes": {
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         },
                         "left_toes": {
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         },
                         "right_knee": {
                              "inward": False,
                              "adequate": False,
                         },
                         "left_knee": {
                              "inward": False,
                              "adequate": False,
                         }
                    }
               if self.weight["type"] == "barbell" and "barbell" not in self.results:
                    self.results["barbell"] = {
                         "left": False,
                         "balanced": False,
                         "right": False
                    }

     # Store the pixels of each landmark that may be required for drawing in a dictionary.
     def get_landmark_pixels(self, image):
         self.pixels = {"left_shoulder":
                    convert_coordinates(self.landmarks["left_shoulder"], image),
                    "right_shoulder":
                    convert_coordinates(self.landmarks["right_shoulder"], image),
                    "left_hip":
                    convert_coordinates(self.landmarks["left_hip"], image),
                    "left_knee":
                    convert_coordinates(self.landmarks["left_knee"], image),
                    "right_knee":
                    convert_coordinates(self.landmarks["right_knee"], image),
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

          # Store angles required for analysis in 'angles' dictionary.
          self.angles["hip_knee_heel_angle"] = calculate_angle(self.landmarks["left_hip"], 
                                                            self.landmarks["left_knee"],
                                                            self.landmarks["left_heel"]
          )
          self.angles["shoulder_hip_knee_angle"] = calculate_angle(self.landmarks["left_shoulder"], 
                                                       self.landmarks["left_hip"], self.landmarks["left_knee"])
          self.angles["left_toes_ankles_angle"] = calculate_angle(self.landmarks["left_toes"],
                                                            self.landmarks["left_ankle"],
                                                            self.landmarks["right_ankle"]
          )
          self.angles["right_toes_ankles_angle"] = calculate_angle(self.landmarks["right_toes"],
                                                            self.landmarks["right_ankle"],
                                                            self.landmarks["left_ankle"]
          )
          # Maintain 'smallest_hip_knee_heel_angle'.
          if "smallest_hip_knee_heel_angle" not in self.angles:
            self.angles["smallest_hip_knee_heel_angle"] = self.angles["hip_knee_heel_angle"]
          else:
               self.angles["smallest_hip_knee_heel_angle"] = min(
               self.angles["smallest_hip_knee_heel_angle"], 
               self.angles["hip_knee_heel_angle"]
            )
               
     # Calculate specific coordinates required for analysis.
     def calculate_distances(self):
         self.distances = {
                    "shoulder_knee_distance": abs(self.landmarks["left_shoulder"][1] - self.landmarks["left_knee"][1]),
                    "feet_distance": np.sqrt((self.landmarks["left_heel"][0] - self.landmarks["right_heel"][0]) ** 2 +
                                        (self.landmarks["left_heel"][1] - self.landmarks["right_heel"][1]) ** 2),
                    "shoulder_distance": np.sqrt((self.landmarks["left_shoulder"][0] - self.landmarks["right_shoulder"][0]) ** 2 +
                                            (self.landmarks["left_shoulder"][1] - self.landmarks["right_shoulder"][1]) ** 2)
                    }
               
     # Calculate specific coordinates required for analysis.
     def calculate_coordinates(self):
          
          # Store specific coordinates required for analysis in 'coordinates' dictionary.
          self.coordinates = self.coordinates if hasattr(self, 'coordinates') else {}

          # Maintain 'largest_left_hip_y'.
          if "largest_left_hip_y" not in self.coordinates:
            self.coordinates["largest_left_hip_y"] = self.landmarks["left_hip"][1]
          else:
               self.coordinates["largest_left_hip_y"] = max(
               self.coordinates["largest_left_hip_y"], 
               self.landmarks["left_hip"][1]
            )
               
          # Maintain 'largest_left_knee_y'.
          if "largest_left_knee_y" not in self.coordinates:
            self.coordinates["largest_left_knee_y"] = self.landmarks["left_knee"][1]
          else:
               self.coordinates["largest_left_knee_y"] = max(
               self.coordinates["largest_left_knee_y"], 
               self.landmarks["left_knee"][1]
            )

     def determine_phase(self):
          if self.view == "left":
               if self.angles["hip_knee_heel_angle"] > 120:
                    return "standing"
               elif self.angles["hip_knee_heel_angle"] < 120:
                    return "squatting"
          # Determine when squat is being performed based on distance between shoulders and knees. If
          # the distance in between the shoulders and knees is less than 0.4, the squat is being 
          # performed.
          # Note: This was hardcoded for my height and has not been adjusted for different heights yet.
          elif self.view == "front":
               if self.distances["shoulder_knee_distance"] >= 0.4:
                    return "standing"
               if self.distances["shoulder_knee_distance"] < 0.4:
                    return "squatting"
              
         
     def analyse_side_view(self, image):
          # Analyse torso position based on torso and shin parallelism by comparing their respective
          # angles. If the difference between the angles is larger than 10, the torso is considered 
          # too upright. If the difference between the angles is less than -10, the torso is 
          # considered as leaning too far forward.
          def analyse_torso_position():
               torso_shin_angle_diff = self.angles["shoulder_hip_knee_angle"] - self.angles["hip_knee_heel_angle"]
               if torso_shin_angle_diff > 10:
                    self.results["torso"]["upright"] += 1
                    self.results["torso"]["current"] = "upright"
                    self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "red")
               elif torso_shin_angle_diff < -10:
                    self.results["torso"]["forward"] += 1
                    self.results["torso"]["current"] = "forward"
                    self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "red")
               else:
                    self.results["torso"]["adequate"] += 1
                    self.results["torso"]["current"] = "adequate"
                    self.draw_line(image, self.pixels["left_shoulder"], self.pixels["left_hip"], "green")

          # Analyse squat depth based on hip, knee and heel coordinates. If the hip does not go 
          # past the knee, the squat is considered too shallow for a conventional squat. If the 
          # angle in between the hip, knee and heel is smaller than 30 degrees, the squat is 
          # considered too deep for a conventional squat.
          def analyse_squat_depth():
               if self.coordinates["largest_left_hip_y"] < self.coordinates["largest_left_knee_y"]:
                   self.results["depth"]["shallow"] == True
                   self.results["depth"]["current"] = "shallow"
                   self.draw_line(image, self.pixels["left_hip"], self.pixels["left_knee"], "orange")
               elif self.angles["smallest_hip_knee_heel_angle"] < 30:
                   self.results["depth"]["deep"] == True
                   self.results["depth"]["current"] = "deep"
                   self.draw_line(image, self.pixels["left_hip"], self.pixels["left_knee"], "red")
               else:
                   self.results["depth"]["adequate"] == True
                   self.results["depth"]["current"] = "adequate"
                   self.draw_line(image, self.pixels["left_hip"], self.pixels["left_knee"], "green")

          # Perform analyses while subject is performing squat.
          if self.determine_phase() == "squatting":
             analyse_torso_position()
             analyse_squat_depth()
             if self.weight["type"] == "barbell":
                 self.results["barbell"]["straight"] = self.analyse_bar_path()
                 print(self.results["barbell"]["straight"])

     def analyse_front_view(self, image):
         
         # Analyse the feet stance based on the distance between the feet and the distance between
         # the shoulders. If the feet are shoulder-width apart or within a 0.2 tolerance, the feet are
         # adequately stanced for a conventional squat.
          def analyse_feet_stance():
               # Feet are too far apart for a conventional squat.
               if self.distances["feet_distance"] > 1.2 * self.distances["shoulder_distance"]:
                    self.results["feet"]["far"] = True
                    self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "red")
                    self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "red")
                    self.draw_cross(image, self.pixels["left_heel_target"], "red")
                    self.draw_cross(image, self.pixels["right_heel_target"], "red")
                    self.draw_circle(image, self.pixels["left_heel"], "red")
                    self.draw_circle(image, self.pixels["right_heel"], "red")
               # Feet are too close together for a conventional squat.
               elif self.distances["feet_distance"] > 0.8 * self.distances["shoulder_distance"]:
                   self.results["feet"]["close"] = True
                   self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "red")
                   self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "red")
                   self.draw_cross(image, self.pixels["left_heel_target"], "red")
                   self.draw_cross(image, self.pixels["right_heel_target"], "red")
                   self.draw_circle(image, self.pixels["left_heel"], "red")
                   self.draw_circle(image, self.pixels["right_heel"], "red")
               # Feet are adequately stanced for a conventional squat.
               else:
                   self.results["feet"]["adequate"] = True
                   self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "green")
                   self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "green")
                   self.draw_cross(image, self.pixels["left_heel_target"], "green")
                   self.draw_cross(image, self.pixels["right_heel_target"], "green")
                   self.draw_circle(image, self.pixels["left_heel"], "green")
                   self.draw_circle(image, self.pixels["left_heel"], "green")

          def analyse_toes():
               if self.angles["left_toes_ankles_angle"] > 140:
                 self.results["left_toes"]["outward"] == True
                 self.draw_circle(image, self.pixels["left_toes"], "red")
               elif self.angles["left_toes_ankles_angle"] < 110:
                    self.results["left_toes"]["inward"] == True
                    self.draw_circle(image, self.pixels["left_toes"], "red")
               else:
                   self.results["left_toes"]["adequate"] == True
                   self.draw_circle(image, self.pixels["left_toes"], "green")

          def analyse_knees():
               if self.landmarks["left_knee"][0] < self.landmarks["left_ankle"][0]:
                    self.results["left_knee"]["inward"] = True
                    self.draw_circle(image, self.pixels["left_knee"], "red")
               else:
                   self.results["left_knee"]["adequate"] = True
                   self.draw_circle(image, self.pixels["left_knee"], "green")

               if self.landmarks["right_knee"][0] > self.landmarks["right_ankle"][0]:
                    self.results["right_knee"]["inward"] = True
                    self.draw_circle(image, self.pixels["right_knee"], "red")
               else:
                   self.results["right_knee"]["adequate"] = True
                   self.draw_circle(image, self.pixels["right_knee"], "green")
         
          if self.determine_phase() == "squatting":
             analyse_feet_stance()
             analyse_toes()
             analyse_knees()

class Deadlift(Analysis):
     def __init__(self, video_path):
          super().__init__(video_path)

     def initialise_results(self):
          if "hip" not in self.results:
               if self.view == "left" or self.view == "right":
                    self.results = {
                         "hip": {
                              "high": 0,
                              "adequate": 0,
                         },
                         "back": {
                              "overextended": False,
                              "adequate": False,
                              "overflexed": False
                         }
                    } 
               if self.view == "front":
                    self.results = {
                         "feet": {
                              "far": False,
                              "adequate": False,
                              "close": False
                         },
                         "right_toes": {
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         },
                         "left_toes": {
                              "outward": False,
                              "adequate": False,
                              "inward": False
                         }
                    }

     def get_landmark_pixels(self, image):
         pass

     def calculate_angles(self):
         self.angles["shoulder_hip_knee_angle"] = calculate_angle(self.landmarks["left_shoulder"], 
                                                            self.landmarks["left_hip"],
                                                            self.landmarks["left_knee"]
          )
     
     def determine_phase(self):
          if self.view == "left" or self.view == "right":
               if self.angles["shoulder_hip_knee_angle"] >= 150:
                    return "standing"
               elif self.angles["shoulder_hip_knee_angle"] < 150:
                    return "deadlifting"
               
     def analyse_side_view(self, image):
         print(self.determine_phase())

     # To do: Feet stance.

     # To do: Toe positioning.
     