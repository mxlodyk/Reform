class DeadliftResults:

    barbell = False
    
    front_view = False
    right_view = False
    left_view = False

    performing_deadlift = False
    completed_deadlift = False
    top_position = False
    bottom_position_reached = False
    top_position_angle = 150
    bottom_position_angle = float('inf')

    # Side view results.
    hips_higher_than_shoulders = False
    shoulders_retracted = False
    back_neutral = False
    back_overextended = False
    #back_rounded = [False, 0]
    knees_locked_at_top = False
    bar_moves_straight = False
    bar_along_leg = False

    def print_results(self):
        if self.hips_higher_than_shoulders:
            print("Hips are higher than shoulders :(")
        else:
            print("Hips are lower than shoulders :)")

        if self.back_overextended:
            print("Back is overextended at top of deadlift.")
        elif self.back_neutral:
            print("Back position is neutral at the top of deadlift.")
        else:
            print("Error determining back score at top of deadlift.")