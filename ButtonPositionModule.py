class ButtonPositioner:
    def __init__(self):
        # add attributes
        self.last_button_clicked = None
        self.counter = 0
        self.large = type('large', (ButtonPositioner,), {'left': 1288, 'right': 1404, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.left = type('left', (ButtonPositioner,), {'left': 1230, 'right': 1308, 'top': 825, 'bottom': 933, 'short': 1200, 'long': 1400})
        self.right = type('right', (ButtonPositioner,), {'left': 1388, 'right': 1504, 'top': 825, 'bottom': 933, 'short': 1200, 'long': 1400})
        self.step_1 = type('step_1', (ButtonPositioner,), {'left': 672, 'right': 757, 'top': 407, 'bottom': 499, 'short': 1200, 'long': 1400})
        self.step_2 = type('step_2', (ButtonPositioner,), {'left': 807, 'right': 887, 'top': 407, 'bottom': 499, 'short': 1200, 'long': 1400})
        self.step_3 = type('step_3', (ButtonPositioner,), {'left': 924, 'right': 1007, 'top': 407, 'bottom': 499, 'short': 1200, 'long': 1400})
        self.step_4 = type('step_4', (ButtonPositioner,), {'left': 1064, 'right': 1137, 'top': 407, 'bottom': 499, 'short': 1200, 'long': 1400})
        self.restart = type('restart', (ButtonPositioner,), {'left': 870, 'right': 945, 'top': 548, 'bottom': 620, 'short': 1200, 'long': 1400})
        self.nav_img = type('nav_img', (ButtonPositioner,), {'left': 1388, 'right': 1504, 'top': 675, 'bottom': 783, 'short': 1200, 'long': 1400})
        self.nav_a = type('nav_a', (ButtonPositioner,), {'left': 930, 'right': 1050, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.nav_b = type('nav_b', (ButtonPositioner,), {'left': 1080, 'right': 1200, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.nav_c = type('nav_c', (ButtonPositioner,), {'left': 1230, 'right': 1350, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.nav_d = type('nav_d', (ButtonPositioner,), {'left': 1388, 'right': 1504, 'top': 725, 'bottom': 833, 'short': 1200, 'long': 1400})
        self.v_cont = type('v_cont', (ButtonPositioner,), {'left': 672, 'right': 1137, 'top': 300, 'bottom': 600, 'short': 1200, 'long': 1400})

    def update_last_button_and_counter(self, type):
        # if last button clicked is this button, then increase counter
        if self.last_button_clicked is type:
            self.counter = self.counter + 1 + (1 if type is self.v_cont else 0)
        # otherwise reset counter
        else:
            self.counter = 0
        # update last button clicked
        self.last_button_clicked = type
        # return true only after accumulated 10 times
        if self.counter >= 10:
            return True

    def check_in_area(self, x, y, z, button_type):
        # redo to make it simpler
        if x > button_type.left and x < button_type.right and y> button_type.top and y< button_type.bottom and z> button_type.short and z < button_type.long:
            # invoke function to increase counter if needed
            print("checked in area")
            return self.update_last_button_and_counter(button_type)
