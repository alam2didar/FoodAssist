import initializer
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic
import res_rc
import sys
import worker_handpos
import worker_evaluator
import steps.step_1_ui as step1Ui
import steps.step_2_ui as step2Ui
import steps.step_3_ui as step3Ui
import steps.step_4_ui as step4Ui

class FoodAssist(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_start.ui', self)

    # hide icons temporarily
    self.status_phone.setHidden(True)
    self.status_watch.setHidden(True)

    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.start_button.clicked.connect(self.button_pressed)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.large) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.start_button.click()

  @qtc.pyqtSlot()
  def button_pressed(self):
    # duplicated but required when interacting with physical mouse
    self.obj.deactivate()
    self.target_ui = Placing_Meat_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  # check if phone and watch are connected
  def onMobileConnected(self):
    self.status_phone.setPixmap(qtg.QPixmap('./resources/Phone On.svg'))
    self.status_watch.setPixmap(qtg.QPixmap('./resources/Watch On.svg'))
    

class Placing_Meat_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_placing_meat.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.my_initializer.detectionParams.connect(self.draw_detection_box)

    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.button_skip.clicked.connect(self.skip_step_detection)
    self.detection_gif = qtg.QMovie('resources/Detecting Icon.gif')
    self.detecting_gif_label.setMovie(self.detection_gif)
    self.detection_gif.start()
    self.step_consistency_counter = 0

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  # paints detection box on UI based on parameter (x,y,w,h) and triggered by event (self.update())
  def paintEvent(self, event):
    print("In Paint event (x,y,w.h): ", self.box_x, self.box_y, self.box_w, self.box_h )
    box_painter = qtg.QPainter(self)
    box_painter.setRenderHint(qtg.QPainter.Antialiasing)
    path = qtg.QPainterPath()
    path.addRoundedRect(qtc.QRectF(self.box_x, self.box_y, self.box_w, self.box_h), 5, 5)
    pen = qtg.QPen(qtc.Qt.GlobalColor.yellow, 5)
    box_painter.setPen(pen)
    box_painter.fillPath(path, qtc.Qt.GlobalColor.transparent)
    box_painter.drawPath(path)
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
    # navigate when 5 consistent detection has occured
    if self.step_consistency_counter == 5:
      self.navigate_to_detected_step()

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.large) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.obj.deactivate()
      self.button_skip.click()

  @qtc.pyqtSlot()
  def skip_step_detection(self):
    self.obj.deactivate()
    self.target_ui = Entry_Step_1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def navigate_to_detected_step(self):
    if self.my_initializer.detected_step == 1:
      self.obj.deactivate()
      self.target_ui = Entry_Step_1_UI(self.my_initializer)
      select_screen_and_show(self.target_ui)
      self.close()

  def draw_detection_box(self, x, y, width, height, step):
    print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
    print('Detected step: ', step)
    self.box_x = x
    self.box_y = y
    self.box_w = width
    self.box_h = height
    self.update()
    if step != 0:
      self.step_consistency_counter += 1
    else:
      self.step_consistency_counter = 0

class Entry_Step_1_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.ui = uic.loadUi('food_assist_gui_entry_step1.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)

    # set qmovie as label
    self.movie_1 = qtg.QMovie('step-gifs/step_1_gesture_1.gif')
    self.label_required_1.setMovie(self.movie_1)
    self.movie_1.start()
    self.movie_2 = qtg.QMovie('step-gifs/step_1_gesture_2.gif')
    self.label_required_2.setMovie(self.movie_2)
    self.movie_2.start()
    self.movie_3 = qtg.QMovie('step-gifs/step_1_gesture_3.gif')
    self.label_required_3.setMovie(self.movie_3)
    self.movie_3.start()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step1Ui.Step_1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.my_initializer.last_class = Entry_Step_1_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

class Entry_Step_2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.ui = uic.loadUi('food_assist_gui_entry_step2.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)

    # set qmovie as label
    self.movie_1 = qtg.QMovie('step-gifs/step_2_gesture_1.gif')
    self.label_required_1.setMovie(self.movie_1)
    self.movie_1.start()
    self.movie_2 = qtg.QMovie('step-gifs/step_2_gesture_3.gif')
    self.label_required_2.setMovie(self.movie_2)
    self.movie_2.start()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step2Ui.Step_2_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.my_initializer.last_class = Entry_Step_2_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

class Entry_Step_3_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.ui = uic.loadUi('food_assist_gui_entry_step3.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)

    # set qmovie as label
    self.movie_1 = qtg.QMovie('step-gifs/step_3_gesture_1.gif')
    self.label_required_1.setMovie(self.movie_1)
    self.movie_1.start()
    self.movie_2 = qtg.QMovie('step-gifs/step_3_gesture_2.gif')
    self.label_required_2.setMovie(self.movie_2)
    self.movie_2.start()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
  
  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_no.click()
  
  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step3Ui.Step_3_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.my_initializer.last_class = Entry_Step_3_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

class Entry_Step_4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.ui = uic.loadUi('food_assist_gui_entry_step4.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)

    # set qmovie as label
    self.movie_1 = qtg.QMovie('step-gifs/step_4_gesture_1.gif')
    self.label_required_1.setMovie(self.movie_1)
    self.movie_1.start()
    self.movie_2 = qtg.QMovie('step-gifs/step_4_gesture_2.gif')
    self.label_required_2.setMovie(self.movie_2)
    self.movie_2.start()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
  
  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step4Ui.Step_4_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.my_initializer.last_class = Entry_Step_4_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

########## Tutorial Ends UI class ##########
class Tutorial_Ends_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_tutorial_ends.ui', self)
    self.button_restart.clicked.connect(self.restart_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_view.clicked.connect(self.button_view_clicked)
    # disable buttons
    self.button_restart.setEnabled(False)
    self.button_exit.setEnabled(False)
    self.button_view.setEnabled(False)
    self.button_view.setHidden(True)
    self.widget_xp.setHidden(True)
    self.widget_score.setHidden(True)
    self.label_text_1.setHidden(False)
    self.label_text_2.setHidden(False)
    self.label_text_1.setText("Congratulation, you have completed all the steps!")
    self.label_text_2.setText("Analyzing your performance...")
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # close file
    self.my_initializer.obj_recorder.close_file()
    # archive file
    self.archive_csv_name = self.my_initializer.obj_recorder.archive_old()
    # reset score_dict, score_sorted_list, score_percent
    self.my_initializer.score_dict = None
    self.my_initializer.score_sorted_list = None
    self.my_initializer.score_percent = None
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
    # create worker evaluator
    create_worker_evaluator(self)

  def onFirstDelayReached(self):
    # hide labels upon delay reached
    self.label_party.setHidden(True)
    # debug - setting evaluation_flag to True
    self.obj_evaluator.evaluate(self.archive_csv_name, True)

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_view.click()

  # def onEvaluationResult(self, success_flag, qualitative_result, troubled_steps, score_percent):
  def onEvaluationResult(self, success_flag, difference_dict, score_dict, score_sorted_list, score_percent):
    # save evaluation result in my_initializer
    self.my_initializer.difference_dict = difference_dict
    self.my_initializer.score_dict = score_dict
    self.my_initializer.score_sorted_list = score_sorted_list
    self.my_initializer.score_percent = score_percent
    # enable buttons
    self.button_restart.setEnabled(True)
    self.button_exit.setEnabled(True)
    # show result
    if success_flag:
      print("reaching point - evaluation successful")
      # enable button_view
      self.button_view.setHidden(False)
      self.button_view.setEnabled(True)
      if score_percent >= 80:
        self.label_text_1.setText("Congratulation! You performed almost like an expert.")
      else:
        # name of the step for the lowest score
        self.label_text_1.setText(f"You seem to need more practice in {score_sorted_list[3][0]}.")
      self.label_text_2.setText("Click the view button to see more details.")
      self.label_text_1.setHidden(False)
      self.label_text_2.setHidden(False)
      # to do - show score percentage
      self.label_text_score.setText(f"{score_percent}%")
      self.widget_xp.setHidden(False)
      self.widget_score.setHidden(False)
    else:
      print("reaching point - evaluation not successful")
      # disable button_view
      self.button_view.setHidden(True)
      self.button_view.setEnabled(False)
      self.label_text_1.setText("Sorry, we weren't able to process your gesture data, please connect mobile app and restart.")
      self.label_text_1.setHidden(False)
      self.label_text_2.setHidden(True)

  # check if button clicked
  def button_view_clicked(self):
    # keep history - not to clean up trash
    # self.obj_evaluator.remove_csv_file(self.archive_csv_name)
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Tutorial_Ends_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()


########## Result Step 1 UI class ##########
class Result_Step1_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step1.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_result after my_initializer is passed
    show_evaluation_result(self, 1)
    # disable left button
    self.button_nav_left.setHidden(True)
    self.button_nav_left.setEnabled(False)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step4_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step1_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step1_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 1 Percent UI class ##########
class Result_Step1_Percent_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step1_percent.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_percent_result after my_initializer is passed
    show_evaluation_percent_result(self, 1)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step2_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step1_Percent_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 2 UI class ##########
class Result_Step2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step2.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_result after my_initializer is passed
    show_evaluation_result(self, 2)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step1_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step2_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step2_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 2 Percent UI class ##########
class Result_Step2_Percent_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step2_percent.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_percent_result after my_initializer is passed
    show_evaluation_percent_result(self, 2)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step2_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step3_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step2_Percent_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 3 UI class ##########
class Result_Step3_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step3.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_result after my_initializer is passed
    show_evaluation_result(self, 3)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step2_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step3_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step3_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()



########## Result Step 3 Percent UI class ##########
class Result_Step3_Percent_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step3_percent.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_percent_result after my_initializer is passed
    show_evaluation_percent_result(self, 3)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step3_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step4_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step3_Percent_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 4 UI class ##########
class Result_Step4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step4.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_result after my_initializer is passed
    show_evaluation_result(self, 4)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step3_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step4_Percent_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step4_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Result Step 4 Percent UI class ##########
class Result_Step4_Percent_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step4_percent.ui', self)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # show_evaluation_percent_result after my_initializer is passed
    show_evaluation_percent_result(self, 4)
    # disable right button
    self.button_nav_right.setHidden(True)
    self.button_nav_right.setEnabled(False)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step4_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.my_initializer.last_class = Result_Step4_Percent_UI
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_left.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_nav_right.click()


########## Menu Default UI class ##########
class Menu_Default_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.ui = uic.loadUi('food_assist_gui_menu_default.ui', self)
    self.button_step1.clicked.connect(self.step1_button_pressed)
    self.button_step2.clicked.connect(self.step2_button_pressed)
    self.button_step3.clicked.connect(self.step3_button_pressed)
    self.button_step4.clicked.connect(self.step4_button_pressed)
    self.button_restart.clicked.connect(self.restart_button_pressed)
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
  
  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.step_1) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.step_2) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.step_3) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.step_4) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.restart_0) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = Confirm_Restart_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def back_button_pressed(self):
    self.obj.deactivate()
    # got to previuos UI
    # self.target_ui = Confirm_Restart_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def step1_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step1Ui.Step_1_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def step2_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step2Ui.Step_2_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def step3_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step3Ui.Step_3_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

  @qtc.pyqtSlot()
  def step4_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = step4Ui.Step_4_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

########## Confirm Restart UI class ##########
class Confirm_Restart_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.ui = uic.loadUi('food_assist_gui_confirm_restart.ui', self)
    self.button_yes.clicked.connect(self.restart_yes_pressed)
    self.button_no.clicked.connect(self.restart_no_pressed)
    
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
  
  def paintEvent(self, event):
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.restart_0) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.step_2) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_no.click()
    
  @qtc.pyqtSlot()
  def restart_yes_pressed(self):
    self.my_initializer.obj_recorder.archive_old()
    self.obj.deactivate()
    self.target_ui = FoodAssist(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def restart_no_pressed(self):
    self.obj.deactivate()
    self.target_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.target_ui)
    self.close()

# Helper Functions
def draw_finger_tip_cursor(self):
  self.finger_tip_x = 0
  self.finger_tip_y = 0
  self.cursor_widget = qtw.QWidget(self)
  cursor_layout = qtw.QHBoxLayout(self.cursor_widget)
  self.cursor_label = qtw.QLabel()
  self.cursor_label.setPixmap(qtg.QPixmap('./resources/Cursor.svg'))
  self.cursor_widget.setStyleSheet('background: transparent;')
  ### FIX me @ Didar
  # QCssParser::parseColorValue: Specified color without alpha value but alpha given: 'rgb 0, 0, 0, 0'
  # https://stackoverflow.com/questions/7667552/qt-widget-with-transparent-background
  ###
  cursor_layout.addWidget(self.cursor_label)
  self.cursor_widget.raise_()

def create_worker_handpos(self, my_initializer):
  # 1 - create Worker and Thread inside the Form # no parent
  self.obj = worker_handpos.WorkerHandPos(my_initializer.my_depth_camera)
  self.thread = qtc.QThread()

  # 2 - Connect Worker`s Signals to Form method slots to post data.
  self.obj.intReady.connect(self.onIntReady)

  # 3 - Move the Worker object to the Thread object
  self.obj.moveToThread(self.thread)

  # 4 - Connect Worker Signals to the Thread slots
  self.obj.finished.connect(self.thread.quit)

  # 5 - Connect Thread started signal to Worker operational slot method
  self.thread.started.connect(self.obj.handPos)

  # * - Thread finished signal will close the app (if needed!)
  # self.thread.finished.connect(app.exit)

  # 6 - Start the thread
  self.thread.start()

def create_worker_evaluator(self):
  # 1 - create Worker and Thread inside the Form # no parent
  self.obj_evaluator = worker_evaluator.WorkerEvaluator()
  self.thread_evaluator = qtc.QThread()

  # 2 - Connect Worker`s Signals to Form method slots to post data.
  self.obj_evaluator.first_delay_reached.connect(self.onFirstDelayReached)
  self.obj_evaluator.evaluation_result.connect(self.onEvaluationResult)

  # 3 - Move the Worker object to the Thread object
  self.obj_evaluator.moveToThread(self.thread_evaluator)

  # 5 - Connect Thread started signal to Worker operational slot method
  self.thread_evaluator.started.connect(self.obj_evaluator.first_delay)

  # * - Thread finished signal will close the app (if needed!)
  # self.thread.finished.connect(app.exit)

  # 6 - Start the thread
  self.thread_evaluator.start()

def show_evaluation_result(self, step_number):
  self.button_restart.clicked.connect(self.restart_button_pressed)
  self.button_exit.clicked.connect(self.exit_button_pressed)
  self.button_nav_left.clicked.connect(self.button_nav_left_clicked)
  self.button_nav_right.clicked.connect(self.button_nav_right_clicked)
  self.label_text_score.setText(f"{self.my_initializer.score_dict[f'step_{step_number}']}%")
  self.label_plot_1_expert.setPixmap(qtg.QPixmap(f'records/plot_1_expert_step_{step_number}.png'))
  self.label_plot_1_user.setPixmap(qtg.QPixmap(f'records/plot_1_user_step_{step_number}.png'))
  text_more_less = [None, None, None]
  difference = [None, None, None]
  for index in range(3):
    difference[index] = self.my_initializer.difference_dict[f'step_{step_number}'][index]
  if difference[0] is None or difference[1] is None or difference[2] is None:
    self.label_trouble.setText(f"You didn't perform any gesture in this step.")
    self.label_analysis_1.setHidden(True)
    self.label_analysis_2.setHidden(True)
    self.label_analysis_3.setHidden(True)
  else:
    for index in range(3):
      if difference[index] > 0:
        text_more_less[index] = 'more'
      else:
        text_more_less[index] = 'less'
        difference[index] = -difference[index]
    # find out worst gesture
    gesture_no = 1
    if difference[1] > difference[0]:
      gesture_no = 2
    if difference[2] > difference[1]:
      gesture_no = 3
    self.label_trouble.setText(f"most troubled: gesture {gesture_no}")
    self.label_analysis_1.setText(f"gesture 1: {difference[0]} time(s) {text_more_less[0]} than the expert")
    self.label_analysis_2.setText(f"gesture 2: {difference[1]} time(s) {text_more_less[1]} than the expert")
    self.label_analysis_3.setText(f"gesture 3: {difference[2]} time(s) {text_more_less[2]} than the expert")

def show_evaluation_percent_result(self, step_number):
  self.button_restart.clicked.connect(self.restart_button_pressed)
  self.button_exit.clicked.connect(self.exit_button_pressed)
  self.button_nav_left.clicked.connect(self.button_nav_left_clicked)
  self.button_nav_right.clicked.connect(self.button_nav_right_clicked)
  self.label_text_score.setText(f"{self.my_initializer.score_dict[f'step_{step_number}']}%")
  self.label_plot_2_expert.setPixmap(qtg.QPixmap(f'records/plot_2_expert_step_{step_number}.png'))
  self.label_plot_2_user.setPixmap(qtg.QPixmap(f'records/plot_2_user_step_{step_number}.png'))
  difference = [None, None, None]
  for index in range(3):
    if self.my_initializer.difference_dict[f'step_{step_number}'][index] is not None:
      difference[index] = self.my_initializer.difference_dict[f'step_{step_number}'][index]
  if difference[0] is None or difference[1] is None or difference[2] is None:
    self.label_analysis_1.setHidden(True)
    self.label_trouble.setText(f"You didn't perform any gesture in this step.")
  else:
    for index in range(3):
      difference[index] = abs(difference[index])
    # find out worst gesture
    gesture_no = 1
    if difference[1] > difference[0]:
      gesture_no = 2
    if difference[2] > difference[1]:
      gesture_no = 3
    self.label_trouble.setHidden(True)
    self.label_analysis_1.setText(f"You need to practice gesture {gesture_no} more in this step.")

# move the app to the secod screen (projector screen)
def select_screen_and_show(ui_class):
  screen_resolution = qtw.QApplication.desktop().screenGeometry(1)
  ui_class.move(qtc.QPoint(screen_resolution.x(), screen_resolution.y()))
  ui_class.showFullScreen()

def change_active_button_color(self, button):
  if button == 1:
    if self.findChild(qtw.QWidget, "button_sub_step2"):
      self.button_sub_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step3"):
      self.button_sub_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step4"):
      self.button_sub_step4.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step1"):
      self.button_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step2"):
      self.button_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step3"):
      self.button_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step4"):
      self.button_step4.setStyleSheet('')
    self.button_sub_step1.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
  if button == 2:
    self.button_sub_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step3"):
      self.button_sub_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step4"):
      self.button_sub_step4.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step1"):
        self.button_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step2"):
      self.button_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step3"):
      self.button_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step4"):
      self.button_step4.setStyleSheet('')
    self.button_sub_step2.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
  if button == 3:
    self.button_sub_step1.setStyleSheet('')
    self.button_sub_step2.setStyleSheet('')
    self.button_sub_step4.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step1"):
        self.button_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step2"):
      self.button_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step3"):
      self.button_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step4"):
      self.button_step4.setStyleSheet('')
    self.button_sub_step3.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
  if button == 4:
    self.button_sub_step1.setStyleSheet('')
    self.button_sub_step2.setStyleSheet('')
    self.button_sub_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step1"):
        self.button_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step2"):
      self.button_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step3"):
      self.button_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step4"):
      self.button_step4.setStyleSheet('')
    self.button_sub_step4.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
  if button == 0:
    if self.findChild(qtw.QWidget, "button_sub_step1"):
      self.button_sub_step1.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step2"):
      self.button_sub_step2.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step3"):
      self.button_sub_step3.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_sub_step4"):
      self.button_sub_step4.setStyleSheet('')
    if self.findChild(qtw.QWidget, "button_step1"):
      self.button_step1.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
    if self.findChild(qtw.QWidget, "button_step2"):
      self.button_step2.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
    if self.findChild(qtw.QWidget, "button_step3"):
      self.button_step3.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())
    if self.findChild(qtw.QWidget, "button_step4"):
      self.button_step4.setStyleSheet(open('./styles/activeButtonStyleGreen.css').read())

def on_substep_button_click(self, substep_button, all_substep=False):
  if not all_substep:
    # set counter to stop the thread when button is clicked
    self.counter = 99
  change_active_button_color(self, substep_button)
  self.player.setVideoOutput(self.ui.VideoWidget)
  self.playlist.setCurrentIndex(substep_button)
  self.player.setPosition(0)
  self.player.play()

def main():
  # initiate app
  app = qtw.QApplication([])
  my_initializer = initializer.Initializer()
  target_ui = FoodAssist(my_initializer)
  select_screen_and_show(target_ui)

  # run the app
  sys.exit(app.exec_())
if __name__ == '__main__':
  main()
