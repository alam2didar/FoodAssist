import initializer
import os
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic, QtMultimedia
import res_rc
import sys
import worker_handpos
import worker_evaluator

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
    self.placeing_meat_ui = Placing_Meat_UI(self.my_initializer)
    # self.placeing_meat_ui.show()
    # self.placeing_meat_ui.showFullScreen()
    select_screen_and_show(self.placeing_meat_ui)
    # self.placeing_meat_ui.get_current_step()
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
    self.my_initializer.detectionParams.connect(self.drawDetectionBox)

    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.button_skip.clicked.connect(self.skip_step_detection)
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
    self.entry_step_1_ui = Entry_Step_1_UI(self.my_initializer)
    # self.entry_step_1_ui.show()
    # self.entry_step_1_ui.showFullScreen()
    select_screen_and_show(self.entry_step_1_ui)
    self.close()
  
  @qtc.pyqtSlot()
  def get_current_step(self):
    # self.show()
    detected_step = 1
    if detected_step == 1:
      self.obj.deactivate()
      self.entry_step_1_ui = Entry_Step_1_UI(self.my_initializer)
      # self.entry_step_1_ui.show()
      # self.entry_step_1_ui.showFullScreen()
      select_screen_and_show(self.entry_step_1_ui)
      self.close()

  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()

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
    self.step_1_ui = Step_1_UI(self.my_initializer)
    # self.step_1_ui.show()
    # self.step_1_ui.showFullScreen()
    select_screen_and_show(self.step_1_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
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
    self.step_2_ui = Step_2_UI(self.my_initializer)
    # self.step_2_ui.show()
    # self.step_2_ui.showFullScreen()
    select_screen_and_show(self.step_2_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
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
    self.step_3_ui = Step_3_UI(self.my_initializer)
    # self.step_3_ui.show()
    # self.step_3_ui.showFullScreen()
    select_screen_and_show(self.step_3_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
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
    self.step_4_ui = Step_4_UI(self.my_initializer)
    # self.step_4_ui.show()
    # self.step_4_ui.showFullScreen()
    select_screen_and_show(self.step_4_ui)
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.close()

########## Step 1 UI class ##########
class Step_1_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 1
    self.my_initializer.obj_recorder.enable_writing()
    self.my_initializer.detectionParams.connect(self.drawDetectionBox)

    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.ui = uic.loadUi('food_assist_gui_step1.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), ".\step-videos\step1.mp4")
    file1 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step1-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step1-substep2.mp4")
    file3 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step1-substep3.mp4")
    file4 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step1-substep4.mp4")
    self.video_files_list = [file0, file1, file2, file3, file4]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    # self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step1.clicked.connect(self.step1)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.button_sub_step2.clicked.connect(self.sub_step2)
    self.button_sub_step3.clicked.connect(self.sub_step3)
    self.button_sub_step4.clicked.connect(self.sub_step4)
    # self.player.pause()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  # paints detection box on UI based on parameter (x,y,w,h) and triggered by event (self.update())
  def paintEvent(self, event):
    box_painter = qtg.QPainter(self)
    box_painter.setRenderHint(qtg.QPainter.Antialiasing)
    path = qtg.QPainterPath()
    path.addRoundedRect(qtc.QRectF(self.box_x, self.box_y, self.box_w, self.box_h), 5, 5)
    pen = qtg.QPen(qtc.Qt.GlobalColor.yellow, 5)
    box_painter.setPen(pen)
    box_painter.fillPath(path, qtc.Qt.GlobalColor.transparent)
    box_painter.drawPath(path)
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_img) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.v_cont) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_controller.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    # call placing meat UI's get_current_step() to 
    # show the appropriate entry step based on the current step

    # for manual navgation, call directly respective entry step
    self.entry_step_2_ui = Entry_Step_2_UI(self.my_initializer)
    # self.entry_step_2_ui.show()
    # self.entry_step_2_ui.showFullScreen()
    select_screen_and_show(self.entry_step_2_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()

  @qtc.pyqtSlot()
  def toggle_video(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
      self.player.pause()
    else:
      self.player.play()
  
  @qtc.pyqtSlot()
  def step1(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(4)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
  
  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()
 
########## Step 2 UI class ##########
class Step_2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 2
    self.my_initializer.obj_recorder.enable_writing()
    self.my_initializer.detectionParams.connect(self.drawDetectionBox)
    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.ui = uic.loadUi('food_assist_gui_step2.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), ".\step-videos\step2.mp4")
    file1 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step2-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step2-substep2-4.mp4")
    self.video_files_list = [file0, file1, file2]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))

    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    # self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step2.clicked.connect(self.step2)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.button_sub_step2.clicked.connect(self.sub_step2)
    self.button_sub_step3.clicked.connect(self.sub_step3)
    self.button_sub_step4.clicked.connect(self.sub_step4)
    # self.player.pause()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  # paints detection box on UI based on parameter (x,y,w,h) and triggered by event (self.update())
  def paintEvent(self, event):
    box_painter = qtg.QPainter(self)
    box_painter.setRenderHint(qtg.QPainter.Antialiasing)
    path = qtg.QPainterPath()
    path.addRoundedRect(qtc.QRectF(self.box_x, self.box_y, self.box_w, self.box_h), 5, 5)
    pen = qtg.QPen(qtc.Qt.GlobalColor.yellow, 5)
    box_painter.setPen(pen)
    box_painter.fillPath(path, qtc.Qt.GlobalColor.transparent)
    box_painter.drawPath(path)
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.obj.deactivate()
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.obj.deactivate()
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_img) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.v_cont) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_controller.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.entry_step_3_ui = Entry_Step_3_UI(self.my_initializer)
    # self.entry_step_3_ui.show()
    # self.entry_step_3_ui.showFullScreen()
    select_screen_and_show(self.entry_step_3_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()

  @qtc.pyqtSlot()
  def toggle_video(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
      self.player.pause()
    else:
      self.player.play()

  @qtc.pyqtSlot()
  def step2(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
  
  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()
        
########## Step 3 UI class ##########
class Step_3_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 3
    self.my_initializer.obj_recorder.enable_writing()
    self.my_initializer.detectionParams.connect(self.drawDetectionBox)
    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.ui = uic.loadUi('food_assist_gui_step3.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), ".\step-videos\step3.mp4")
    file1 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step3-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step3-substep2.mp4")
    file3 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step3-substep3-4.mp4")
    self.video_files_list = [file0, file1, file2, file3]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))

    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    # self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step3.clicked.connect(self.step3)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.button_sub_step2.clicked.connect(self.sub_step2)
    self.button_sub_step3.clicked.connect(self.sub_step3)
    self.button_sub_step4.clicked.connect(self.sub_step4)
    self.player.pause()

    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  # paints detection box on UI based on parameter (x,y,w,h) and triggered by event (self.update())
  def paintEvent(self, event):
    box_painter = qtg.QPainter(self)
    box_painter.setRenderHint(qtg.QPainter.Antialiasing)
    path = qtg.QPainterPath()
    path.addRoundedRect(qtc.QRectF(self.box_x, self.box_y, self.box_w, self.box_h), 5, 5)
    pen = qtg.QPen(qtc.Qt.GlobalColor.yellow, 5)
    box_painter.setPen(pen)
    box_painter.fillPath(path, qtc.Qt.GlobalColor.transparent)
    box_painter.drawPath(path)
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_img) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.v_cont) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_controller.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.entry_step_4_ui = Entry_Step_4_UI(self.my_initializer)
    # self.entry_step_4_ui.show()
    # self.entry_step_4_ui.showFullScreen()
    select_screen_and_show(self.entry_step_4_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()

  @qtc.pyqtSlot()
  def toggle_video(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
      self.player.pause()
    else:
      self.player.play()
  
  @qtc.pyqtSlot()
  def step3(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
  
  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()

########## Step 4 UI class ##########
class Step_4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 4
    self.my_initializer.obj_recorder.enable_writing()
    self.my_initializer.detectionParams.connect(self.drawDetectionBox)
    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0
  
    self.ui = uic.loadUi('food_assist_gui_step4.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), ".\step-videos\step4.mp4")
    file1 = os.path.join(os.path.dirname(__file__), ".\step-videos\Step4-Final step.mp4")
    self.video_files_list = [file0, file1]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    # self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step4.clicked.connect(self.step4)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.player.pause()
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)
  
  # paints detection box on UI based on parameter (x,y,w,h) and triggered by event (self.update())
  def paintEvent(self, event):
    box_painter = qtg.QPainter(self)
    box_painter.setRenderHint(qtg.QPainter.Antialiasing)
    path = qtg.QPainterPath()
    path.addRoundedRect(qtc.QRectF(self.box_x, self.box_y, self.box_w, self.box_h), 5, 5)
    pen = qtg.QPen(qtc.Qt.GlobalColor.yellow, 5)
    box_painter.setPen(pen)
    box_painter.fillPath(path, qtc.Qt.GlobalColor.transparent)
    box_painter.drawPath(path)
    self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_a) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_b) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_img) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.nav_d) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.v_cont) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_controller.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.tutorial_ends_ui = Tutorial_Ends_UI(self.my_initializer)
    # self.tutorial_ends_ui.show()
    # self.tutorial_ends_ui.showFullScreen()
    select_screen_and_show(self.tutorial_ends_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()

  @qtc.pyqtSlot()
  def toggle_video(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
      self.player.pause()
    else:
      self.player.play()
  
  @qtc.pyqtSlot()
  def step4(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
  
  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()

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

  def onEvaluationResult(self, success_flag, qualitative_result, troubled_steps, score_percent):
    # enable buttons
    self.button_restart.setEnabled(True)
    self.button_exit.setEnabled(True)
    # show result
    if success_flag:
      print("reaching point - evaluation successful")
      self.button_view.setHidden(False)
      self.button_view.setEnabled(True)
      if qualitative_result:
        self.label_text_1.setText("Congratualation! You performed almost like an expert.")
      else:
        self.label_text_1.setText(f"Your seemed to have trouble in the following steps:\n {troubled_steps}")
      self.label_text_2.setText("Click the view button to see more details.")
      self.label_text_1.setHidden(False)
      self.label_text_2.setHidden(False)
      # to do - show score percentage
      self.label_text_4.setText(f"{score_percent}%")
      self.widget_xp.setHidden(False)
      self.widget_score.setHidden(False)
    else:
      print("reaching point - evaluation not successful")
      self.button_view.setHidden(True)
      self.label_text_1.setText("Sorry, we weren't able to process your data, please connect mobile app and restart.")
      self.label_text_1.setHidden(False)
      self.label_text_2.setHidden(True)

  # check if button clicked
  def button_view_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step1 = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.result_step1)
    self.close()


  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    # self.food_assist.show()
    # self.food_assist.showFullScreen()
    select_screen_and_show(self.food_assist)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    # self.menu_default_ui.showFullScreen()
    select_screen_and_show(self.menu_default_ui)
    self.close()


########## Result Step 1 UI class ##########
class Result_Step1_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.ui = uic.loadUi('food_assist_gui_result_step1.ui', self)
    show_evaluation_result(self, 1)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step4 = Result_Step4_UI(self.my_initializer)
    select_screen_and_show(self.result_step4)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step2 = Result_Step2_UI(self.my_initializer)
    select_screen_and_show(self.result_step2)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    select_screen_and_show(self.food_assist)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.menu_default_ui)
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
    show_evaluation_result(self, 2)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step1 = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.result_step1)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step3 = Result_Step3_UI(self.my_initializer)
    select_screen_and_show(self.result_step3)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    select_screen_and_show(self.food_assist)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.menu_default_ui)
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
    show_evaluation_result(self, 3)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step2 = Result_Step2_UI(self.my_initializer)
    select_screen_and_show(self.result_step2)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step4 = Result_Step4_UI(self.my_initializer)
    select_screen_and_show(self.result_step4)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    select_screen_and_show(self.food_assist)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.menu_default_ui)
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
    show_evaluation_result(self, 4)
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # draw finger-tip cursor
    draw_finger_tip_cursor(self)
    # Hand tracking thread
    create_worker_handpos(self, self.my_initializer)

  @qtc.pyqtSlot()
  def button_nav_left_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step3 = Result_Step3_UI(self.my_initializer)
    select_screen_and_show(self.result_step3)
    self.close()

  @qtc.pyqtSlot()
  def button_nav_right_clicked(self):
    # redirects to Result_Step1_UI
    # deactivate worker
    self.obj.deactivate()
    self.result_step1 = Result_Step1_UI(self.my_initializer)
    select_screen_and_show(self.result_step1)
    self.close()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    select_screen_and_show(self.food_assist)
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    select_screen_and_show(self.menu_default_ui)
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
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.button_c) and self.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_restart.click()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    self.my_initializer.obj_recorder.archive_old()
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    # self.food_assist.show()
    # self.food_assist.showFullScreen()
    select_screen_and_show(self.food_assist)
    self.close()

  @qtc.pyqtSlot()
  def step1_button_pressed(self):
    self.obj.deactivate()
    self.step_1_ui = Step_1_UI(self.my_initializer)
    # self.step_1_ui.show()
    # self.step_1_ui.showFullScreen()
    select_screen_and_show(self.step_1_ui)
    self.close()

  @qtc.pyqtSlot()
  def step2_button_pressed(self):
    self.obj.deactivate()
    self.step_2_ui = Step_2_UI(self.my_initializer)
    # self.step_2_ui.show()
    # self.step_2_ui.showFullScreen()
    select_screen_and_show(self.step_2_ui)
    self.close()

  @qtc.pyqtSlot()
  def step3_button_pressed(self):
    self.obj.deactivate()
    self.step_3_ui = Step_3_UI(self.my_initializer)
    # self.step_3_ui.show()
    # self.step_3_ui.showFullScreen()
    select_screen_and_show(self.step_3_ui)
    self.close()

  @qtc.pyqtSlot()
  def step4_button_pressed(self):
    self.obj.deactivate()
    self.step_4_ui = Step_4_UI(self.my_initializer)
    # self.step_4_ui.show()
    # self.step_4_ui.showFullScreen()
    select_screen_and_show(self.step_4_ui)
    self.close()

# Helper Functions
def draw_finger_tip_cursor(self):
  self.finger_tip_x = 0
  self.finger_tip_y = 0
  self.cursor_widget = qtw.QWidget(self)
  cursor_layout = qtw.QHBoxLayout(self.cursor_widget)
  self.cursor_label = qtw.QLabel()
  self.cursor_label.setPixmap(qtg.QPixmap('./resources/Cursor.svg'))
  self.cursor_widget.setStyleSheet('background-color: rgb(0, 0, 0, 0)')
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

# move the app to the secod screen (projector screen)
def show_evaluation_result(self, step_number):
  self.button_restart.clicked.connect(self.restart_button_pressed)
  self.button_exit.clicked.connect(self.exit_button_pressed)
  self.button_nav_left.clicked.connect(self.button_nav_left_clicked)
  self.button_nav_right.clicked.connect(self.button_nav_right_clicked)
  self.label_plot_1_expert.setPixmap(qtg.QPixmap(f'records/expertfig_1_step_{step_number}.png'))
  self.label_plot_2_expert.setPixmap(qtg.QPixmap(f'records/expertfig_2_step_{step_number}.png'))
  self.label_plot_1_user.setPixmap(qtg.QPixmap(f'records/myfig_1_step_{step_number}.png'))
  self.label_plot_2_user.setPixmap(qtg.QPixmap(f'records/myfig_2_step_{step_number}.png'))
  self.label_text_1.setText(f"Step {step_number}")
  self.label_text_2.setHidden(True)

# move the app to the secod screen (projector screen)
def select_screen_and_show(ui_class):
  screen_resolution = qtw.QApplication.desktop().screenGeometry(1)
  ui_class.move(qtc.QPoint(screen_resolution.x(), screen_resolution.y()))
  ui_class.showFullScreen()

def main():
  # initiate app
  app = qtw.QApplication([])
  my_initializer = initializer.Initializer()
  food_assist = FoodAssist(my_initializer)
  select_screen_and_show(food_assist)

  # run the app
  sys.exit(app.exec_())
if __name__ == '__main__':
  main()
