import analysis
import numpy as np
from helpers import calculate_angle
from helpers import convert_coordinates

class Deadlift(analysis.Analysis):
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
          if self.weight == "barbell":
            if not self.analyse_bar_path():
                self.results["barbell"]["straight"] == False