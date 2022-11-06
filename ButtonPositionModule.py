class ButtonPositioner:
    def __init__(self):
        # add attributes
        self.last_button_clicked = None
        self.counter = 0
        self.large = type('large', (ButtonPositioner,), {'left': 1288, 'right': 1404, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.button_a = type('button_a', (ButtonPositioner,), {'left': 1365, 'right': 1446, 'top': 858, 'bottom': 937, 'short': 1200, 'long': 1400})
        self.button_b = type('button_b', (ButtonPositioner,), {'left': 1482, 'right': 1560, 'top': 851, 'bottom': 939, 'short': 1200, 'long': 1400})
        self.button_c = type('button_c', (ButtonPositioner,), {'left': 885, 'right': 975, 'top': 548, 'bottom': 620, 'short': 1200, 'long': 1400})
        self.button_d = type('button_d', (ButtonPositioner,), {'left': 980, 'right': 1070, 'top': 548, 'bottom': 620, 'short': 1200, 'long': 1400})
        self.restart_0 = type('restart_0', (ButtonPositioner,), {'left': 870, 'right': 945, 'top': 548, 'bottom': 620, 'short': 1200, 'long': 1400})
        self.step_1 = type('step_1', (ButtonPositioner,), {'left': 745, 'right': 815, 'top': 405, 'bottom': 475, 'short': 1200, 'long': 1400})
        self.step_2 = type('step_2', (ButtonPositioner,), {'left': 873, 'right': 944, 'top': 405, 'bottom': 475, 'short': 1200, 'long': 1400})
        self.step_3 = type('step_3', (ButtonPositioner,), {'left': 998, 'right': 1063, 'top': 405, 'bottom': 475, 'short': 1200, 'long': 1400})
        self.step_4 = type('step_4', (ButtonPositioner,), {'left': 1125, 'right': 1200, 'top': 405, 'bottom': 475, 'short': 1200, 'long': 1400})
        self.nav_img = type('nav_img', (ButtonPositioner,), {'left': 1472, 'right': 1559, 'top': 627, 'bottom': 713, 'short': 1200, 'long': 1400})
        self.nav_a = type('nav_a', (ButtonPositioner,), {'left': 1175, 'right': 1255, 'top': 732, 'bottom': 818, 'short': 1200, 'long': 1400})
        self.nav_b = type('nav_b', (ButtonPositioner,), {'left': 1275, 'right': 1356, 'top': 733, 'bottom': 813, 'short': 1200, 'long': 1400})
        self.nav_c = type('nav_c', (ButtonPositioner,), {'left': 1375, 'right': 1457, 'top': 733, 'bottom': 815, 'short': 1200, 'long': 1400})
        self.nav_d = type('nav_d', (ButtonPositioner,), {'left': 1475, 'right': 1559, 'top': 733, 'bottom': 815, 'short': 1200, 'long': 1400})
        self.button_de = type('button_de', (ButtonPositioner,), {'left': 600, 'right': 678, 'top': 509, 'bottom': 591, 'short': 1200, 'long': 1400})
        self.button_en = type('button_en', (ButtonPositioner,), {'left': 717, 'right': 808, 'top': 509, 'bottom': 591, 'short': 1200, 'long': 1400})
        # to do - calibrate buttons
        self.button_left_shoulder = type('button_left_shoulder', (ButtonPositioner,), {'left': 1085, 'right': 1161, 'top': 515, 'bottom': 593, 'short': 1200, 'long': 1400})
        self.button_right_shoulder = type('button_right_shoulder', (ButtonPositioner,), {'left': 1234, 'right': 1312, 'top': 515, 'bottom': 593, 'short': 1200, 'long': 1400})
        self.v_play = type('v_play', (ButtonPositioner,), {'left': 1182, 'right': 1240, 'top': 565, 'bottom': 615, 'short': 1200, 'long': 1400})
        self.v_pause = type('v_pause', (ButtonPositioner,), {'left': 1280, 'right': 1334, 'top': 565, 'bottom': 615, 'short': 1200, 'long': 1400})

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
