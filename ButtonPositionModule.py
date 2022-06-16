class ButtonPositioner:
    def __init__(self):
        # add attributes
        self.last_button_clicked = None
        self.counter = 0
        # left_button area
        self.left_button_left = 320
        self.left_button_right = 450
        self.left_button_top = 400
        self.left_button_bottom = 455
        self.left_button_short = 1200
        self.left_button_long = 1250
        # right_button area
        self.right_button_left = 480
        self.right_button_right = 600
        self.right_button_top = 400
        self.right_button_bottom = 455
        self.right_button_short = 1200
        self.right_button_long = 1250
        # step_1_button area
        self.step_1_button_left = 215
        self.step_1_button_right = 255
        self.step_1_button_top = 395
        self.step_1_button_bottom = 455
        self.step_1_button_short = 1200
        self.step_1_button_long = 1250
        # step_2_button area
        self.step_2_button_left = 280
        self.step_2_button_right = 320
        self.step_2_button_top = 395
        self.step_2_button_bottom = 455
        self.step_2_button_short = 1200
        self.step_2_button_long = 1250
        # step_3_button area
        self.step_3_button_left = 340
        self.step_3_button_right = 370
        self.step_3_button_top = 395
        self.step_3_button_bottom = 455
        self.step_3_button_short = 1200
        self.step_3_button_long = 1250
        # step_4_button area
        self.step_4_button_left = 385
        self.step_4_button_right = 425
        self.step_4_button_top = 395
        self.step_4_button_bottom = 455
        self.step_4_button_short = 1200
        self.step_4_button_long = 1250
        # restart_button area
        self.restart_button_left = 300
        self.restart_button_right = 350
        self.restart_button_top = 435
        self.restart_button_bottom = 460
        self.restart_button_short = 1200
        self.restart_button_long = 1250

    def update_last_button_and_counter(self, type):
        # if last button clicked is this button, then increase counter
        if self.last_button_clicked is type:
            self.counter = self.counter + 1
        # otherwise reset counter
        else:
            self.counter = 0
        # update last button clicked
        self.last_button_clicked = type
        # return true only after accumulated 20 times
        if self.counter>=20:
            return True

    def check_in_area(self, x, y, z, type):
        if type == "left":
            if x >= self.left_button_left and x <= self.left_button_right and \
            y>= self.left_button_top and y<= self.left_button_bottom and \
            z>= self.left_button_short and z <= self.left_button_long:
                return self.update_last_button_and_counter(type)
        if type == "right":
            # check if in area
            if x >= self.right_button_left and x <= self.right_button_right and \
            y>= self.right_button_top and y<= self.right_button_bottom and \
            z>= self.right_button_short and z <= self.right_button_long:
                return self.update_last_button_and_counter(type)
        if type == "step_1":
            if x >= self.step_1_button_left and x <= self.step_1_button_right and \
            y>= self.step_1_button_top and y<= self.step_1_button_bottom and \
            z>= self.step_1_button_short and z <= self.step_1_button_long:
                return self.update_last_button_and_counter(type)
        if type == "step_2":
            if x >= self.step_2_button_left and x <= self.step_2_button_right and \
            y>= self.step_2_button_top and y<= self.step_2_button_bottom and \
            z>= self.step_2_button_short and z <= self.step_2_button_long:
                return self.update_last_button_and_counter(type)
        if type == "step_3":
            if x >= self.step_3_button_left and x <= self.step_3_button_right and \
            y>= self.step_3_button_top and y<= self.step_3_button_bottom and \
            z>= self.step_3_button_short and z <= self.step_3_button_long:
                return self.update_last_button_and_counter(type)
        if type == "step_4":
            if x >= self.step_4_button_left and x <= self.step_4_button_right and \
            y>= self.step_4_button_top and y<= self.step_4_button_bottom and \
            z>= self.step_4_button_short and z <= self.step_4_button_long:
                return self.update_last_button_and_counter(type)
        if type == "restart":
            if x >= self.restart_button_left and x <= self.restart_button_right and \
            y>= self.restart_button_top and y<= self.restart_button_bottom and \
            z>= self.restart_button_short and z <= self.restart_button_long:
                return self.update_last_button_and_counter(type)
