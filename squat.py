import analysis
import numpy as np
from helpers import calculate_angle
from helpers import convert_coordinates

class Squat(analysis.Analysis):

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
                         },
                         "right_knee": {
                              "current": "",
                              "inward": False,
                              "adequate": False,
                         },
                         "left_knee": {
                              "current": "",
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

     def analyse_front_view(self, image):
         
         # Analyse the feet stance based on the distance between the feet and the distance between
         # the shoulders. If the feet are shoulder-width apart or within a 0.2 tolerance, the feet are
         # adequately stanced for a conventional squat.
          def analyse_feet_stance():
               # Feet are too far apart for a conventional squat.
               if self.distances["feet_distance"] > 1.2 * self.distances["shoulder_distance"]:
                    self.results["feet"]["far"] = True
                    self.results["feet"]["current"] = "far"
                    self.draw_dashed_line(image, self.pixels["left_shoulder"], self.pixels["left_heel_target"], "red")
                    self.draw_dashed_line(image, self.pixels["right_shoulder"], self.pixels["right_heel_target"], "red")
                    self.draw_cross(image, self.pixels["left_heel_target"], "red")
                    self.draw_cross(image, self.pixels["right_heel_target"], "red")
                    self.draw_circle(image, self.pixels["left_heel"], "red")
                    self.draw_circle(image, self.pixels["right_heel"], "red")
               # Feet are too close together for a conventional squat.
               elif self.distances["feet_distance"] > 0.8 * self.distances["shoulder_distance"]:
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
                   self.draw_circle(image, self.pixels["left_heel"], "green")

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

          def analyse_knees():

               if self.landmarks["left_knee"][0] < self.landmarks["left_ankle"][0]:
                    self.results["left_knee"]["inward"] = True
                    self.results["left_knee"]["current"] = "inward"
                    self.draw_circle(image, self.pixels["left_knee"], "red")
               else:
                   self.results["left_knee"]["adequate"] = True
                   self.results["left_knee"]["current"] = "adequate"
                   self.draw_circle(image, self.pixels["left_knee"], "green")

               if self.landmarks["right_knee"][0] > self.landmarks["right_ankle"][0]:
                    self.results["right_knee"]["inward"] = True
                    self.results["right_knee"]["current"] = "inward"
                    self.draw_circle(image, self.pixels["right_knee"], "red")
               else:
                   self.results["right_knee"]["adequate"] = True
                   self.results["right_knee"]["current"] = "adequate"
                   self.draw_circle(image, self.pixels["right_knee"], "green")
         
          if self.determine_phase() == "squatting":
             analyse_feet_stance()
             analyse_toes()
             analyse_knees()
             if self.weight == "barbell":
                if not self.analyse_bar_path():
                    self.results["barbell"]["straight"] == False