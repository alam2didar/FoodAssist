import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
from PyQt5 import uic

import foodAssist as fa


########## Result Step X Page X UI class ##########
class Result_StepX_PageX_UI(qtw.QWidget):
    def __init__(self, my_initializer, step_number, page_number):
        super().__init__()
        self.step_number = step_number
        self.page_number = page_number
        self.ui = uic.loadUi(f'ui/{my_initializer.lang}_{my_initializer.hand}_result_step{self.step_number}_page{self.page_number}.ui', self)
        # pass on my_initializer
        self.my_initializer = my_initializer
        self.my_initializer.current_step = None
        # show_evaluation_result after my_initializer is passed
        self.show_evaluation_result(self.step_number, self.page_number)
        if self.step_number == 1 and self.page_number == 1:
            # disable left button
            self.button_nav_left.setHidden(True)
            self.button_nav_left.setEnabled(False)
        if self.step_number == 4 and self.page_number == 4:
            # disable right button
            self.button_nav_right.setHidden(True)
            self.button_nav_right.setEnabled(False)
        # draw finger-tip cursor
        fa.draw_finger_tip_cursor(self)
        # Hand tracking thread
        self.my_initializer.hand_position.connect(self.onHandPositionArrival)
        self.my_initializer.obj.reset_counter()

    @qtc.pyqtSlot()
    def button_nav_left_clicked(self):
        self.my_initializer.hand_position.disconnect()
        target_step_number, target_page_number = self.get_previous_page(self.step_number, self.page_number)
        self.target_ui = Result_StepX_PageX_UI(self.my_initializer, target_step_number, target_page_number)
        fa.select_screen_and_show(self.target_ui)
        self.close()

    @qtc.pyqtSlot()
    def button_nav_right_clicked(self):
        self.my_initializer.hand_position.disconnect()
        target_step_number, target_page_number = self.get_next_page(self.step_number, self.page_number)
        self.target_ui = Result_StepX_PageX_UI(self.my_initializer, target_step_number, target_page_number)
        fa.select_screen_and_show(self.target_ui)
        self.close()

    @qtc.pyqtSlot()
    def exit_button_pressed(self):
        self.my_initializer.hand_position.disconnect()
        self.my_initializer.last_class = Result_StepX_PageX_UI
        # save step_number and page_number to my_initializer
        self.my_initializer.step_number = self.step_number
        self.my_initializer.page_number = self.page_number
        self.target_ui = fa.Menu_Default_UI(self.my_initializer)
        fa.select_screen_and_show(self.target_ui)
        self.close()

    def paintEvent(self, event):
        self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

    # check if the button is touched
    def onHandPositionArrival(self, x, y, z, counter, cursor_x, cursor_y):
        # draw cursor for finger tip
        self.finger_tip_x = cursor_x
        self.finger_tip_y = cursor_y
        self.update()
        if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.button_b) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
            self.button_exit.click()
        if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.button_c) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
            self.button_nav_left.click()
        if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.button_d) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
            self.button_nav_right.click()


    def show_evaluation_result(self, step_number, page_number):
        self.button_exit.clicked.connect(self.exit_button_pressed)
        self.button_nav_left.clicked.connect(self.button_nav_left_clicked)
        self.button_nav_right.clicked.connect(self.button_nav_right_clicked)
        # calculate the average score
        # self.label_text_score.setText(f"{self.my_initializer.step_score_dict[f'step_{step_number}']}%")
        self.label_plot_1.setPixmap(qtg.QPixmap(f'records/count_plot_step_{step_number}_gesture_{page_number}.png'))
        # change icon_reaction_1 based on score for gesture (page_number)
        if self.my_initializer.score_dict[f'step_{step_number}'][page_number-1] > 0.66:
            self.icon_reaction_1.setPixmap(qtg.QPixmap(f'ui/resources/Happy Face.png'))
        elif self.my_initializer.score_dict[f'step_{step_number}'][page_number-1] > 0.33:
            self.icon_reaction_1.setPixmap(qtg.QPixmap(f'ui/resources/Neutral Face.png'))
        else:
            self.icon_reaction_1.setPixmap(qtg.QPixmap(f'ui/resources/Unhappy Face.png'))


    def get_previous_page(self, step_number, page_number):
        if (page_number - 1) % 4 == 0:
            target_page_number = 4
            if (step_number - 1) % 4 == 0:
                target_step_number = 4
            else:
                target_step_number = (step_number - 1) % 4
        else:
            target_page_number = (page_number - 1) % 4
            target_step_number = step_number
        return target_step_number, target_page_number

    def get_next_page(self, step_number, page_number):
        target_page_number = 1 if page_number == 4 else page_number + 1
        if target_page_number == 1:
            target_step_number = step_number + 1
            if step_number == 4:
                target_step_number = 1
        else:
            target_step_number = step_number
        print('step, page:', target_step_number, target_page_number)
        return target_step_number, target_page_number