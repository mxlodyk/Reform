class DeadliftResults:

    front_view = False
    right_view = False
    left_view = False

    performing_deadlift = False
    completed_deadlift = False
    top_position = False
    bottom_position = False

    # Side view results.
    hips_higher_than_shoulders = False
    shoulders_retracted = False
    back_neutral = False
    back_overextended = False
    back_rounded = False
    knees_locked_at_top = False
    bar_moves_straight = False
    bar_along_leg = False

    def print_results(self):
        if self.hips_higher_than_shoulders:
            print("Hips are higher than shoulders :(")
        else:
            print("Hips are lower than shoulders :)")