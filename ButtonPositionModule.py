class ButtonPositioner:
    def __init__(self):
        # add attributes
        self.last_button_clicked = None
        self.counter = 0
        self.left = type('left', (ButtonPositioner,), {'left': 410, 'right': 470, 'top': 400, 'bottom': 455, 'short': 1200, 'long': 1400})
        self.right = type('right', (ButtonPositioner,), {'left': 480, 'right': 560, 'top': 350, 'bottom': 430, 'short': 1200, 'long': 1400})
        self.step_1 = type('step_1', (ButtonPositioner,), {'left': 215, 'right': 255, 'top': 395, 'bottom': 455, 'short': 1200, 'long': 1400})
        self.step_2 = type('step_2', (ButtonPositioner,), {'left': 280, 'right': 320, 'top': 395, 'bottom': 455, 'short': 1200, 'long': 1400})
        self.step_3 = type('step_3', (ButtonPositioner,), {'left': 340, 'right': 370, 'top': 395, 'bottom': 455, 'short': 1200, 'long': 1400})
        self.step_4 = type('step_4', (ButtonPositioner,), {'left': 385, 'right': 425, 'top': 395, 'bottom': 455, 'short': 1200, 'long': 1400})
        self.restart = type('restart', (ButtonPositioner,), {'left': 320, 'right': 350, 'top': 320, 'bottom': 460, 'short': 1200, 'long': 1400})

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

    def check_in_area(self, x, y, z, button_type):
        # redo to make it simpler
        if x > button_type.left and x < button_type.right and y> button_type.top and y< button_type.bottom and z> button_type.short and z < button_type.long:
            # invoke function to increase counter if needed
            # return self.update_last_button_and_counter(button_type)
            pass
