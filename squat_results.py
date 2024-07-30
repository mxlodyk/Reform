class SquatResults:

    front_view = False
    right_view = False
    left_view = False

    performing_squat = False
    completed_squat = False
    deepest_squat_angle = float('inf')

    feet_too_far = False
    feet_too_close = False
    left_toes_too_outward = False
    right_toes_too_outward = False
    left_toes_too_inward = False
    right_toes_too_inward = False
    left_knee_inward = False
    right_knee_inward = False
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
            elif self.left_toes_too_inward and self.right_toes_too_inward:
                print("Toes too inward.")
            elif self.left_toes_too_inward and not self.right_toes_too_inward:
                print("Left toes too inward.")
            elif self.right_toes_too_inward and not self.left_toes_too_inward:
                print("Right toes too inward.")
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

        if self.left_view or self.right_view:
            if self.too_shallow:
                print("Squat is too shallow.")
            elif self.too_deep:
                print("Squat is too deep.")
            else:
                print("Squat depth is adequate.")
            if self.torso_too_upright > self.torso_too_forward and self.torso_too_upright > self.torso_adequate:
                print("Torso is too upright.")
            elif self.torso_too_forward > self.torso_too_upright and self.torso_too_forward > self.torso_adequate:
                print("Torso is leaning too far forward.")
            else:
                print("Torso is adequate.")