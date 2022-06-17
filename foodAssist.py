import sys
import time
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic, QtMultimedia
from PyQt5 import QtTest
import res_rc
from handPosGlobal import HandPosGlobal
import os
import worker_handpos
import worker_evaluator
import initializer

class FoodAssist(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    uic.loadUi('food_assist_gui_start.ui', self)
     # enable custom window hint
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)

    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()

    self.start_button.clicked.connect(self.button_pressed)

    # Hand tracking thread
    create_worker_handpos(self)

  def check_button_press(self):
    HandPosGlobal().dispatchEvent("HandPosition")

  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    # if x >= 1310 and x <=1370 and y>= 600 and y<= 660 and z>= 960 and z <= 1115:
    # if x >= 480 and x <= 600 and y>= 400 and y<= 455 and z>= 1200 and z <= 1250 and self.obj.worker_activated:
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.right) and self.obj.worker_activated:
      self.obj.deactivate()
      time.sleep(0.20)
      self.start_button.click()

  @qtc.pyqtSlot()
  def button_pressed(self):
    # duplicated but required when interacting with physical mouse
    self.obj.deactivate()
    self.placeing_meat_ui = Placing_Meat_UI(self.my_initializer)
    # self.placeing_meat_ui.show()
    self.placeing_meat_ui.showFullScreen()
    # self.placeing_meat_ui.get_current_step()
    self.close()


class Placing_Meat_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
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
    create_worker_handpos(self)

  def paintEvent(self, event):
    qp = qtg.QPainter(self)
    br = qtg.QBrush(qtg.QColor(255, 255, 255, 255))  
    qp.setBrush(br)   
    # qp.drawRect(qtc.QRect(self.begin, self.end)) 
    qp.drawRect(self.box_x, self.box_y, self.box_w, self.box_h)

  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Placing Meat - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    # if x >= 480 and x <= 600 and y>= 400 and y<= 455 and z>= 1200 and z <= 1250 and self.obj.worker_activated and c > 50:
    if self.obj.button_positioner.check_in_area(x, y, z, self.obj.button_positioner.right) and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_skip.click()

  @qtc.pyqtSlot()
  def skip_step_detection(self):
    self.obj.deactivate()
    self.entry_step_1_ui = Entry_Step_1_UI(self.my_initializer)
    # self.entry_step_1_ui.show()
    self.entry_step_1_ui.showFullScreen()
    self.close()
  
  @qtc.pyqtSlot()
  def get_current_step(self):
    # self.show()
    detected_step = 1
    if detected_step == 1:
      self.obj.deactivate()
      self.entry_step_1_ui = Entry_Step_1_UI(self.my_initializer)
      # self.entry_step_1_ui.show()
      self.entry_step_1_ui.showFullScreen()
      self.close()

  def drawDetectionBox(self, x, y, width, height, step):
        print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        # qp.drawRect(QtCore.QRect(self.begin, self.end))
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
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_entry_step1.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Entry Step 1 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.step_1_ui = Step_1_UI(self.my_initializer)
    # self.step_1_ui.show()
    self.step_1_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
    self.close()

class Entry_Step_2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_entry_step2.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Entry Step 2 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.step_2_ui = Step_2_UI(self.my_initializer)
    # self.step_2_ui.show()
    self.step_2_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
    self.close()

class Entry_Step_3_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_entry_step3.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Entry Step 3 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_no.click()
  
  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.step_3_ui = Step_3_UI(self.my_initializer)
    # self.step_3_ui.show()
    self.step_3_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
    self.close()

class Entry_Step_4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_entry_step4.ui', self)
    self.button_yes.clicked.connect(self.yes_button_pressed)
    self.button_no.clicked.connect(self.no_button_pressed)
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Entry Step 4 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_yes.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_no.click()

  @qtc.pyqtSlot()
  def yes_button_pressed(self):
    self.obj.deactivate()
    self.step_4_ui = Step_4_UI(self.my_initializer)
    # self.step_4_ui.show()
    self.step_4_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def no_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
    self.close()

########## Step 1 UI class ##########
class Step_1_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 1
    self.my_initializer.obj_recorder.enable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_step1.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), "video-step1.mp4")
    file1 = os.path.join(os.path.dirname(__file__), "Step1-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), "Step1-substep2.mp4")
    file3 = os.path.join(os.path.dirname(__file__), "Step1-substep3.mp4")
    file4 = os.path.join(os.path.dirname(__file__), "Step1-substep4.mp4")
    self.video_files_list = [file0, file1, file2, file3, file4]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    self.player.setVideoOutput(self.ui.VideoWidget)
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
    self.player.pause()
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Step 1 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_exit.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    # call placing meat UI's get_current_step() to 
    # show the appropriate entry step based on the current step

    # for manual navgation, call directly respective entry step
    self.entry_step_2_ui = Entry_Step_2_UI(self.my_initializer)
    # self.entry_step_2_ui.show()
    self.entry_step_2_ui.showFullScreen()
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
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
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.playlist.setCurrentIndex(4)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
 
########## Step 2 UI class ##########
class Step_2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 2
    self.my_initializer.obj_recorder.enable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_step2.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), "video-step2.mp4")
    file1 = os.path.join(os.path.dirname(__file__), "Step2-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), "Step2-substep2-4.mp4")
    self.video_files_list = [file0, file1, file2]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    self.player.setVideoOutput(self.ui.VideoWidget)
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
    self.player.pause()
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Step 2 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_exit.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.entry_step_3_ui = Entry_Step_3_UI(self.my_initializer)
    # self.entry_step_3_ui.show()
    self.entry_step_3_ui.showFullScreen()
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
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
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
        
########## Step 3 UI class ##########
class Step_3_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 3
    self.my_initializer.obj_recorder.enable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_step3.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0= os.path.join(os.path.dirname(__file__), "video-step3.mp4")
    file1 = os.path.join(os.path.dirname(__file__), "Step3-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), "Step3-substep2.mp4")
    file3 = os.path.join(os.path.dirname(__file__), "Step3-substep3-4.mp4")
    self.video_files_list = [file0, file1, file2, file3]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    self.player.setVideoOutput(self.ui.VideoWidget)
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
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Step 3 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_exit.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.entry_step_4_ui = Entry_Step_4_UI(self.my_initializer)
    # self.entry_step_4_ui.show()
    self.entry_step_4_ui.showFullScreen()
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
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
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step2(self):
    self.playlist.setCurrentIndex(2)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step3(self):
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step4(self):
    self.playlist.setCurrentIndex(3)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)

########## Step 4 UI class ##########
class Step_4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 4
    self.my_initializer.obj_recorder.enable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_step4.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0= os.path.join(os.path.dirname(__file__), "video-step4.mp4")
    file1 = os.path.join(os.path.dirname(__file__), "Step4-Final step.mp4")
    self.video_files_list = [file0, file1]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step4.clicked.connect(self.step4)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.player.pause()
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Step 4 - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_next.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_exit.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.obj.deactivate()
    self.tutorial_ends_ui = Tutorial_Ends_UI(self.my_initializer)
    # self.tutorial_ends_ui.show()
    self.tutorial_ends_ui.showFullScreen()
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
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
    self.playlist.setCurrentIndex(0)
    self.player.setPosition(0)
    self.player.play()
  @qtc.pyqtSlot()
  def sub_step1(self):
    self.playlist.setCurrentIndex(1)
    self.player.setPosition(0)
    self.player.play()

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)

########## Tutorial Ends UI class ##########
class Tutorial_Ends_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_tutorial_ends.ui', self)
    self.button_restart.clicked.connect(self.restart_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_view.clicked.connect(self.button_view_clicked)
    self.label_new_plot_1.setHidden(True)
    self.label_new_plot_2.setHidden(True)
    self.label_new_plot_3.setHidden(True)
    create_worker_handpos(self)

    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    # close file
    self.my_initializer.obj_recorder.close_file()
    # archive file
    self.archive_file_name = self.my_initializer.obj_recorder.archive_old()
    # create worker evaluator
    create_worker_evaluator(self)
    # debug - setting evaluation_flag to True
    self.obj_evaluator.evaluate(self.archive_file_name, True)

  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Tutorial Ends - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "left") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_restart.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "right") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_exit.click()

  # check if message received
  def button_view_clicked(self):
    # hide labels upon clicking
    self.start_label.setHidden(True)
    self.label.setHidden(True)
    # show result
    if self.obj_evaluator.evaluation_finished:
      print("reaching point - displaying result")
      # set image and text to show result
      self.label_new_plot_1.setHidden(False)
      self.label_new_plot_2.setHidden(False)
      self.label_new_plot_3.setHidden(False)
      new_pixmap_1 = qtg.QPixmap(self.obj_evaluator.fig_1_name)
      self.label_new_plot_1.setPixmap(new_pixmap_1)
      new_pixmap_2 = qtg.QPixmap(self.obj_evaluator.fig_2_name)
      self.label_new_plot_2.setPixmap(new_pixmap_2)
      self.label_new_plot_3.setText(self.obj_evaluator.result_text)
    else:
      self.label_new_plot_3.setHidden(False)
      print("Evaluation not finished or not possible")
      self.label_new_plot_3.setText("Evaluation not possible or not finished")

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    # self.food_assist.show()
    self.food_assist.showFullScreen()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    # deactivate worker
    self.obj.deactivate()
    self.menu_default_ui = Menu_Default_UI(self.my_initializer)
    # self.menu_default_ui.show()
    self.menu_default_ui.showFullScreen()
    self.close()


########## Menu Default UI class ##########
class Menu_Default_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = None
    self.my_initializer.obj_recorder.disable_writing()
    self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
    self.ui = uic.loadUi('food_assist_gui_menu_default.ui', self)
    self.button_step1.clicked.connect(self.step1_button_pressed)
    self.button_step2.clicked.connect(self.step2_button_pressed)
    self.button_step3.clicked.connect(self.step3_button_pressed)
    self.button_step4.clicked.connect(self.step4_button_pressed)
    self.button_restart.clicked.connect(self.restart_button_pressed)
    create_worker_handpos(self)
  
  # check if the button is touched
  def onIntReady(self, x, y, z, c):
    print(f'In Tutorial Ends - UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {c}')
    if self.obj.button_positioner.check_in_area(x, y, z, "step_1") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_step1.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "step_2") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_step2.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "step_3") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_step3.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "step_4") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_step4.click()
    if self.obj.button_positioner.check_in_area(x, y, z, "restart") and self.obj.worker_activated and c > 50:
      self.obj.deactivate()
      time.sleep(0.20)
      self.button_restart.click()

  @qtc.pyqtSlot()
  def restart_button_pressed(self):
    self.my_initializer.obj_recorder.archive_old()
    self.obj.deactivate()
    self.food_assist = FoodAssist(self.my_initializer)
    # self.food_assist.show()
    self.food_assist.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def step1_button_pressed(self):
    self.obj.deactivate()
    self.step_1_ui = Step_1_UI(self.my_initializer)
    # self.step_1_ui.show()
    self.step_1_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def step2_button_pressed(self):
    self.obj.deactivate()
    self.step_2_ui = Step_2_UI(self.my_initializer)
    # self.step_2_ui.show()
    self.step_2_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def step3_button_pressed(self):
    self.obj.deactivate()
    self.step_3_ui = Step_3_UI(self.my_initializer)
    # self.step_3_ui.show()
    self.step_3_ui.showFullScreen()
    self.close()

  @qtc.pyqtSlot()
  def step4_button_pressed(self):
    self.obj.deactivate()
    self.step_4_ui = Step_4_UI(self.my_initializer)
    # self.step_4_ui.show()
    self.step_4_ui.showFullScreen()
    self.close()

# Helper Functions
def create_worker_handpos(self):
  # 1 - create Worker and Thread inside the Form # no parent
  self.obj = worker_handpos.WorkerHandPos()
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

  # 3 - Move the Worker object to the Thread object
  self.obj_evaluator.moveToThread(self.thread_evaluator)

  # * - Thread finished signal will close the app (if needed!)
  # self.thread.finished.connect(app.exit)

  # 6 - Start the thread
  self.thread_evaluator.start()

def main():
  # initiate app
  app = qtw.QApplication([])
  my_initializer = initializer.Initializer()
  food_assist = FoodAssist(my_initializer)
  # food_assist.show()
  food_assist.showFullScreen()
  # run the app
  sys.exit(app.exec_())
if __name__ == '__main__':
  main()


