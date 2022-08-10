class ButtonPositioner:
    def __init__(self):
        # add attributes
        self.last_button_clicked = None
        self.counter = 0
        self.large = type('large', (ButtonPositioner,), {'left': 1255, 'right': 1365, 'top': 707, 'bottom': 822, 'short': 1100, 'long': 1300})
        self.button_a = type('button_a', (ButtonPositioner,), {'left': 1321, 'right': 1399, 'top': 833, 'bottom': 915, 'short': 1100, 'long': 1300})
        self.button_b = type('button_b', (ButtonPositioner,), {'left': 1441, 'right': 1514, 'top': 835, 'bottom': 910, 'short': 1100, 'long': 1300})
        self.button_c = type('button_c', (ButtonPositioner,), {'left': 869, 'right': 950, 'top': 545, 'bottom': 622, 'short': 1100, 'long': 1300})
        self.button_d = type('button_d', (ButtonPositioner,), {'left': 965, 'right': 1040, 'top': 541, 'bottom': 621, 'short': 1100, 'long': 1300})
        # self.restart_0 = type('restart_0', (ButtonPositioner,), {'left': 0, 'right': 0, 'top': 0, 'bottom': 0, 'short': 1100, 'long': 1300})
        self.step_1 = type('step_1', (ButtonPositioner,), {'left': 717, 'right': 795, 'top': 375, 'bottom': 450, 'short': 1100, 'long': 1300})
        self.step_2 = type('step_2', (ButtonPositioner,), {'left': 845, 'right': 925, 'top': 375, 'bottom': 450, 'short': 1100, 'long': 1300})
        self.step_3 = type('step_3', (ButtonPositioner,), {'left': 972, 'right': 1058, 'top': 375, 'bottom': 450, 'short': 1100, 'long': 1300})
        self.step_4 = type('step_4', (ButtonPositioner,), {'left': 1102, 'right': 1182, 'top': 375, 'bottom': 450, 'short': 1100, 'long': 1300})
        self.nav_img = type('nav_img', (ButtonPositioner,), {'left': 1448, 'right': 1525, 'top': 610, 'bottom': 689, 'short': 1100, 'long': 1300})
        self.nav_a = type('nav_a', (ButtonPositioner,), {'left': 1144, 'right': 1222, 'top': 712, 'bottom': 792, 'short': 1100, 'long': 1300})
        self.nav_b = type('nav_b', (ButtonPositioner,), {'left': 1245, 'right': 1321, 'top': 712, 'bottom': 792, 'short': 1100, 'long': 1300})
        self.nav_c = type('nav_c', (ButtonPositioner,), {'left': 1348, 'right': 1421, 'top': 712, 'bottom': 792, 'short': 1100, 'long': 1300})
        self.nav_d = type('nav_d', (ButtonPositioner,), {'left': 1447, 'right': 1522, 'top': 712, 'bottom': 792, 'short': 1100, 'long': 1300})
        self.button_de = type('button_de', (ButtonPositioner,), {'left': 575, 'right': 657, 'top': 480, 'bottom': 570, 'short': 1100, 'long': 1300})
        self.button_en = type('button_en', (ButtonPositioner,), {'left': 695, 'right': 783, 'top': 483, 'bottom': 575, 'short': 1100, 'long': 1300})
        self.button_left_hand = type('button_left_hand', (ButtonPositioner,), {'left': 1053, 'right': 1135, 'top': 495, 'bottom': 570, 'short': 1100, 'long': 1300})
        self.button_right_hand = type('button_right_hand', (ButtonPositioner,), {'left': 1203, 'right': 1285, 'top': 492, 'bottom': 571, 'short': 1100, 'long': 1300})
        self.v_play = type('v_play', (ButtonPositioner,), {'left': 1150, 'right': 1210, 'top': 541, 'bottom': 594, 'short': 1100, 'long': 1300})
        self.v_pause = type('v_pause', (ButtonPositioner,), {'left': 1255, 'right': 1310, 'top': 541, 'bottom': 594, 'short': 1100, 'long': 1300})

    def update_last_button_and_counter(self, button_type):
        # if last button clicked is this button, then increase counter
        if self.last_button_clicked is button_type:
            self.counter = self.counter + 1
        # otherwise reset counter
        else:
            self.counter = 0
        # update last button clicked
        self.last_button_clicked = button_type
        # return true only after accumulated 5 times
        if self.counter > 4:
            self.counter = 0
            return True

    def check_in_area(self, x, y, z, button_type):
        # redo to make it simpler
        if x > button_type.left and x < button_type.right and y> button_type.top and y< button_type.bottom and z> button_type.short and z < button_type.long:
            # invoke function to increase counter if needed
            print("checked in area")
            return self.update_last_button_and_counter(button_type)
