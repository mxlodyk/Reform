class SquatResults:

    barbell = False
    bar_path_straight = False

    front_view = False
    right_view = False
    left_view = False

    performing_squat = False
    completed_squat = False
    deepest_squat_angle = float('inf')
    tallest_squat_height = float('-inf')

    feet_too_far = False
    feet_too_close = False
    # Replace with counters and update dependant code.
    left_toes_too_inward = False
    left_toes_too_outward = False
    right_toes_too_inward = False
    right_toes_too_outward = False
    # left_toes_too_inward = 0
    # left_toes_too_outward = 0
    # left_toes_adequate = 0
    # right_toes_too_inward = 0
    # right_toes_too_outward = 0
    # right_toes_adequate = 0
    left_knee_inward = 0
    left_knee_adequate = 0
    right_knee_inward = 0
    right_knee_adequate = 0
    torso_too_forward = 0
    torso_too_upright = 0
    torso_adequate = 0
    too_shallow = False
    too_deep = False

    def __init__(self):
        pass

    # Print results
    def print_results(self):
        if self.front_view:
            if self.feet_too_far:
                print("Feet are too far apart.")
            elif self.feet_too_close:
                print("Feet are too close together.")
            elif not self.feet_too_close and not self.feet_too_far:
                print("Feet are adequately stanced.")
            else:
                print("Error printing result of knee analysis.")

            if self.left_toes_too_outward and self.right_toes_too_outward:
                print("Toes are pointed too outward.")
            elif self.left_toes_too_outward and not self.right_toes_too_outward:
                print("Toes are pointed too outward.")
            elif self.right_toes_too_outward and not self.left_toes_too_outward:
                print("Right toes are pointed too outward.")
            elif self.left_toes_too_inward and self.right_toes_too_inward:
                print("Toes are pointed too inward.")
            elif self.left_toes_too_inward and not self.right_toes_too_inward:
                print("Left toes are pointed too inward.")
            elif self.right_toes_too_inward and not self.left_toes_too_inward:
                print("Right toes are pointed too inward.")
            elif not self.right_toes_too_inward and not self.right_toes_too_outward and not self.left_toes_too_inward and not self.left_toes_too_outward:
                print("Toes are adequately pointed.")
            else:
                print("Error printing result of toe analysis.")

            if self.left_knee_inward > self.left_knee_adequate and self.right_knee_inward > self.right_knee_adequate:
                print("Knees moved inward.")
            elif self.left_knee_inward > self.left_knee_adequate and not self.right_knee_inward > self.right_knee_adequate:
                print("Left knee moved inward.")
            elif self.right_knee_inward > self.right_knee_adequate and not self.left_knee_inward > self.left_knee_adequate:
                print("Right knee moved inward.")
            elif self.right_knee_adequate > self.right_knee_inward and self.left_knee_adequate > self.left_knee_inward:
                print("Knee motion is adequate.")
            else:
                print("Error printing result of knee analysis.")

        if self.left_view or self.right_view:
            if self.too_shallow:
                print("Squat depth is too shallow.")
            elif self.too_deep:
                print("Squat depth is too deep.")
            else:
                print("Squat depth is adequate.")
            if self.torso_too_upright > self.torso_too_forward and self.torso_too_upright > self.torso_adequate:
                print("Torso is too upright.")
            elif self.torso_too_forward > self.torso_too_upright and self.torso_too_forward > self.torso_adequate:
                print("Torso is leaning too far forward.")
            else:
                print("Torso is adequately positioned.")