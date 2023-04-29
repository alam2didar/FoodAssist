import os
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic, QtMultimedia

import foodAssist as fa

########## Step 2 UI class ##########
class Step_2_UI(qtw.QWidget):
  def __init__(self, my_initializer):
    super().__init__()
    # pass on my_initializer
    self.my_initializer = my_initializer
    self.my_initializer.current_step = 2
    self.my_initializer.detection_params.connect(self.draw_detection_box)
    self.box_x = 0
    self.box_y = 0
    self.box_w = 0
    self.box_h = 0

    self.ui = uic.loadUi(f'ui/{my_initializer.lang}_{my_initializer.hand}_step2.ui', self)
    self.hide_video_controller_buttons(True)
    self.play_button_opacity = qtw.QGraphicsOpacityEffect()
    self.pause_button_opacity = qtw.QGraphicsOpacityEffect()
    self.button_video_play.setGraphicsEffect(self.play_button_opacity)
    self.button_video_pause.setGraphicsEffect(self.pause_button_opacity)
    self.button_video_play.setAutoFillBackground(True)
    self.button_video_pause.setAutoFillBackground(True)
    self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
    self.playlist = QtMultimedia.QMediaPlaylist()
    file0 = os.path.join(os.path.dirname(__file__), f"..\step-videos\{my_initializer.lang}\{my_initializer.hand}\step2.mp4")
    file1 = os.path.join(os.path.dirname(__file__), f"..\step-videos\{my_initializer.lang}\{my_initializer.hand}\Step2-substep1.mp4")
    file2 = os.path.join(os.path.dirname(__file__), f"..\step-videos\{my_initializer.lang}\{my_initializer.hand}\Step2-substep2.mp4")
    self.video_files_list = [file0, file1, file2]
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
    self.button_video_play.clicked.connect(self.play_video_pressed)
    self.button_video_pause.clicked.connect(self.pause_video_pressed)
    self.button_step2.clicked.connect(self.step2)
    self.button_sub_step1.clicked.connect(self.sub_step1)
    self.button_sub_step2.clicked.connect(self.sub_step2)
    # self.player.pause()

    # draw finger-tip cursor
    fa.draw_finger_tip_cursor(self)
    # Hand tracking thread
    self.my_initializer.hand_position.connect(self.onHandPositionArrival)
    self.my_initializer.gesture_to_ui.connect(self.onGestureToUiArrival)
    self.my_initializer.obj.reset_counter()

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
    # Stop the thread when button is clicked (counter is 99)
    if self.counter == 99:
      self.counter = 0
      if self.timer:
        self.timer.stop()
        self.timer.deleteLater()
    else:
      self.counter = self.counter + 1
      if self.counter < 12 and self.highlight_on_off_array[self.counter]:
        if self.button == 1:
            self.button_sub_step1.setStyleSheet(open('./styles/activeButtonStyleYellow.css').read())
        if self.button == 2:
            self.button_sub_step2.setStyleSheet(open('./styles/activeButtonStyleYellow.css').read())
        if self.button == 3:
            self.button_next.setStyleSheet(open('./styles/activeButtonStyleYellow.css').read())
      else:
        if self.button == 1:
          self.button_sub_step1.setStyleSheet('')
        if self.button == 2:
          self.button_sub_step2.setStyleSheet('')
        if self.button == 3:
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
    if self.finger_tip_y >= 560:
      self.cursor_widget.move(self.finger_tip_x, self.finger_tip_y)

  # check if the button is touched
  def onGestureToUiArrival(self, result_gesture):
    self.image_gesture.setPixmap(qtg.QPixmap(f':/img/gesture{result_gesture}.png'))
    if self.my_initializer.lang == 'en':
      self.text_gesture.setText(f'Detected: Gesture {result_gesture}')
    else:
      self.text_gesture.setText(f'Erkannt: Geste {result_gesture}')

  # check if the button is touched
  def onHandPositionArrival(self, x, y, z, counter, cursor_x, cursor_y):
    # draw cursor for finger tip
    self.finger_tip_x = cursor_x
    self.finger_tip_y = cursor_y
    self.update()
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.button_a) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_next.click()
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.button_b) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_exit.click()
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.nav_img) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_step2.click()
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.nav_c) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step1.click()
      self.button_sub_step1.setEnabled(False)
      qtc.QTimer.singleShot(5000, lambda: self.button_sub_step1.setDisabled(False))
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.nav_d) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_sub_step2.click()
      self.button_sub_step2.setEnabled(False)
      qtc.QTimer.singleShot(5000, lambda: self.button_sub_step2.setDisabled(False))
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.v_play) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_play.click()
    if self.my_initializer.obj.button_positioner.check_in_area(x, y, z, self.my_initializer.obj.button_positioner.v_pause) and self.my_initializer.obj.worker_activated and counter > self.my_initializer.interval_between_uis:
      self.button_video_pause.click()

  @qtc.pyqtSlot()
  def next_button_pressed(self):
    self.my_initializer.hand_position.disconnect()
    self.target_ui = fa.Entry_Step_3_UI(self.my_initializer)
    fa.select_screen_and_show(self.target_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()
  
  @qtc.pyqtSlot()
  def exit_button_pressed(self):
    self.my_initializer.hand_position.disconnect()
    self.my_initializer.last_class = Step_2_UI
    self.target_ui = fa.Menu_Default_UI(self.my_initializer)
    fa.select_screen_and_show(self.target_ui)
    self.player = QtMultimedia.QMediaPlayer()
    self.close()

  # QMediaPlayer::StoppedState	0	
  # QMediaPlayer::PlayingState	1	
  # QMediaPlayer::PausedState	2
  @qtc.pyqtSlot()
  def play_video_pressed(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
      self.player.play()
      self.alternate_play_pause_buttons(False)
    if self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
      self.player.setPosition(0)
      self.player.play()
      self.alternate_play_pause_buttons(False)
  
  @qtc.pyqtSlot()
  def pause_video_pressed(self):
    if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
      self.player.pause()
      self.alternate_play_pause_buttons(True)

  @qtc.pyqtSlot()
  def step2(self):
    fa.on_substep_button_click(self, 0, True)
    self.hide_video_controller_buttons(False)
    self.alternate_play_pause_buttons(False)
    
  @qtc.pyqtSlot()
  def sub_step1(self):
    fa.on_substep_button_click(self, 1)
    self.hide_video_controller_buttons(False)
    self.alternate_play_pause_buttons(False)

  @qtc.pyqtSlot()
  def sub_step2(self):
    fa.on_substep_button_click(self, 2)
    self.hide_video_controller_buttons(False)
    self.alternate_play_pause_buttons(False)

  @qtc.pyqtSlot()
  def on_position_changed(self):
    if self.player.duration() - self.player.position() < 100:
      self.player.setPosition(self.player.duration() - 10)
  
  # QMediaPlayer::EndOfMedia	7	
  # Playback has reached the end of the current media. The player is in the StoppedState.
  # ref: https://doc.qt.io/qt-5/qmediaplayer.html#mediaStatus-prop
  @qtc.pyqtSlot()
  def on_media_status_changed(self):
    if self.player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
      self.alternate_play_pause_buttons(True)
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
  
  def hide_video_controller_buttons(self, is_hide):
    self.button_video_play.setHidden(is_hide)
    self.button_video_pause.setHidden(is_hide)
  
  def alternate_play_pause_buttons(self, enable_play):
    if enable_play:
      self.button_video_play.setEnabled(True)
      self.button_video_pause.setEnabled(False)
      self.play_button_opacity.setOpacity(1.0)
      self.pause_button_opacity.setOpacity(0.3)
    else:
      self.button_video_play.setEnabled(False)
      self.button_video_pause.setEnabled(True)
      self.play_button_opacity.setOpacity(0.3)
      self.pause_button_opacity.setOpacity(1.0)
