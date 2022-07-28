import os
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic, QtMultimedia

import foodAssist as fa

########## Step 4 UI class ##########
class Step_4_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 4
    self.my_initializer.obj_recorder.enable_writing()
    self.my_initializer.detectionParams.connect(self.draw_detection_box)
    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0
  
    self.ui = uic.loadUi('food_assist_gui_step4.ui', self)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), "..\step-videos\step4.mp4")
    file1 = os.path.join(os.path.dirname(__file__), "..\step-videos\Step4-Final step.mp4")
    self.video_files_list = [file0, file1]
    for f in self.video_files_list:
      self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(f)))
    self.playlist.setCurrentIndex(1)
    self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
    # self.player.setVideoOutput(self.ui.VideoWidget)
    self.player.setPlaylist(self.playlist)
    self.player.setMuted(True)
    self.player.positionChanged.connect(self.on_position_changed)
    self.player.mediaStatusChanged.connect(self.on_media_status_changed)
    self.button_next.clicked.connect(self.next_button_pressed)
    self.button_exit.clicked.connect(self.exit_button_pressed)
    self.button_video_controller.clicked.connect(self.toggle_video)
    self.button_step4.clicked.connect(self.step4)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.player.pause()
    # draw finger-tip cursor
    fa.draw_finger_tip_cursor(self)
    # Hand tracking thread
    fa.create_worker_handpos(self, self.my_initializer)

    # configure animate button 
    self.counter = 0
    self.highlight_on_off_array = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    self.button = 1
    # start initial timer to animate
    self.timer = qtc.QTimer()
    self.timer.start(350)
    self.timer.timeout.connect(self.animate_button)

  # keep the order of the if statements 
  def animate_button(self):
        self.counter = self.counter + 1
        # set counter (to 100) to stop the thread when button is clicked
        if self.counter < 12 and self.highlight_on_off_array[self.counter] or self.counter == 100:
          if self.button == 1:
             self.button_sub_step1.setStyleSheet(open('./styles/activeButtonStyle.css').read())
          if self.button == 2:
             self.button_next.setStyleSheet(open('./styles/activeButtonStyle.css').read())
       # set counter to stop the thread when button is clicked (100)
        elif self.counter != 100:
          if self.button == 1:
            self.button_sub_step1.setStyleSheet('')
          if self.button == 2:
             self.button_next.setStyleSheet('')
        # this check must be at the end
        if self.counter >= 12:
          self.counter = 0
          self.timer.stop()
          self.timer.deleteLater()
  
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
    self.target_ui = fa.Tutorial_Ends_UI(self.my_initializer)
    fa.select_screen_and_show(self.target_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.obj.deactivate()
    self.target_ui = fa.Menu_Default_UI(self.my_initializer)
    fa.select_screen_and_show(self.target_ui)
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
    fa.on_substep_button_click(self, 0, True)

  @qtc.pyqtSlot()
  def sub_step1(self):
    fa.on_substep_button_click(self, 1)

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
          self.player.setPosition(self.player.duration() - 10)
  
  @qtc.pyqtSlot()
  def on_media_status_changed(self):
    if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
      current_video_index = self.playlist.currentIndex()
      self.button = current_video_index + 1
      self.counter = 0
      self.timer = qtc.QTimer(self)
      self.timer.timeout.connect(self.animate_button)
      self.timer.start(250)
  
  def draw_detection_box(self, x, y, width, height, step):
        # print('Detection box parameters from model: (x, y, w, h)', x, y, width, height)
        print('Detected step: ', step)
        self.box_x = x
        self.box_y = y
        self.box_w = width
        self.box_h = height
        self.update()