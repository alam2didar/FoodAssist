# import sys
import sys
from threading import Timer
import time
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
from PyQt5 import uic, QtMultimedia
from PyQt5 import QtTest
import res_rc
from handPosGlobal import HandPosGlobal
import os
import worker

# load UI files for each step
# form_1, base_1 = uic.loadUiType('food_assist_gui_step1.ui')
# form_2, base_2 = uic.loadUiType('food_assist_gui_step2.ui')
# form_3, base_3 = uic.loadUiType('food_assist_gui_step3.ui')
# form_4, base_4 = uic.loadUiType('food_assist_gui_step4.ui')

def create_worker(self):
  # 1 - create Worker and Thread inside the Form # no parent
  self.obj = worker.Worker()
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


class FoodAssist(qtw.QWidget):
   def __init__(self):
      super().__init__()
      uic.loadUi('food_assist_gui_start.ui', self)
      # enable custom window hint
      self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
      flagTrackHand = False
      # flagTrackHand = True

      # disable (but not hide) close button  
      # self.setWindowFlags(self.windowFlags() & ~qtc.Qt.WindowCloseButtonHint)
      # self.setWindowFlag(qtc.Qt.WindowCloseButtonHint, False)
      
      # HandPosGlobal().addEventListener("HandPosition", self.button_pressed)
      self.resize(1680, 1050)
      # self.show()
   #    self.setWindowTitle("Food-Assist: UI")
   #    self.setLayout(qtw.QVBoxLayout())

   #    my_label = qtw.QLabel("Example Text")
   #    my_label.setFont(qtg.QFont('Consolas', 18, 3, True))
   #    self.layout().addWidget(my_label)
   #  #   button
      # button_check_green = qtw.QPushButton("Green check button",
      #   clicked = lambda: press_it())
      # self.start_button.clicked = self.press_it()
      # self.start_button.clicked.connect(self.check_button_press)
      self.start_button.clicked.connect(self.button_pressed)
      self.start_label.adjustSize()

      
      # self.start_button.click()
      #perform a programmatic click
      # self.start_button.click()
            
   #    self.layout().addWidget(button_check_green)

      # Hand tracking thread
      if flagTrackHand:
        create_worker(self)


   def check_button_press(self):
         HandPosGlobal().dispatchEvent("HandPosition")

   #  check if the button is touched
   def onIntReady(self, x, y, z, g):
        print(f'In UI recived: X: {x}, Y:{y}, Z:{z}, Counter: {g}')
        # if x >= 1310 and x <=1370 and y>= 600 and y<= 660 and z>= 960 and z <= 1115:
        if x >= 560 and x <=600 and y>= 425 and y<= 460 and z>= 1110 and z <= 1130 and self.obj.worker_activated:
          self.obj.worker_activated = False
          time.sleep(0.20)
          self.start_button.click()

   @qtc.pyqtSlot()
   def button_pressed(self):
      # self.start_label.setText(f'Start button pressed!!')
      
      self.placeing_meat_ui = Placing_Meat_UI()
      self.placeing_meat_ui.show()
      # self.placeing_meat_ui.get_current_step()
      self.close()



      # self.show()
    #   font = QFont()
    #   font.setFamily("Arial")
    #   font.setPointSize(16)
    #   self.label.setFont(font)
    #   self.label.move(50,20)

# app = qtw.QApplication([])
# mw = MainWindow()
# # mw.show()
# # run the app
# app.exec_()


class Placing_Meat_UI(qtw.QWidget):
      def __init__(self):
        super().__init__()
        self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
        self.ui = uic.loadUi('food_assist_gui_placing_meat.ui', self)
        self.resize(1680, 1050)
        self.button_skip.clicked.connect(self.skip_step_detection)
        create_worker(self)
      
       #  check if the button is touched
      def onIntReady(self, x, y, z, g):
        print(f'In Step Placing Meat - UI recived: X: {x}, Y:{y}, Z:{z}, Gesture: {g}')
        if x >= 560 and x <= 600 and y>= 425 and y<= 460 and z>= 1110 and z <= 1130 and self.obj.worker_activated and g > 50:
          self.obj.worker_activated = False
          time.sleep(0.20)
          self.button_skip.click()

      @qtc.pyqtSlot()
      def skip_step_detection(self):
        self.entry_step_1_ui = Entry_Step_1_UI()
        self.entry_step_1_ui.show()
        self.close()
      
      @qtc.pyqtSlot()
      def get_current_step(self):
        # self.show()
        detected_step = 1
        if detected_step is 1:
          self.entry_step_1_ui = Entry_Step_1_UI()
          self.entry_step_1_ui.show()
          self.close()

class Entry_Step_1_UI(qtw.QWidget):
      def __init__(self):
        super().__init__()
        self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
        self.ui = uic.loadUi('food_assist_gui_entry_step1.ui', self)
        self.resize(1680, 1050)
        self.button_yes.clicked.connect(self.yes_button_pressed)
        self.button_no.clicked.connect(self.no_button_pressed)
        create_worker(self)
      
       #  check if the button is touched
      def onIntReady(self, x, y, z, g):
        print(f'In Step 1 - UI recived: X: {x}, Y:{y}, Z:{z}, Gesture: {g}')
        if x >= 480 and x <= 510 and y>= 430 and y<= 460 and z>= 1110 and z <= 1130 and self.obj.worker_activated and g > 50:
          self.obj.worker_activated = False
          time.sleep(0.20)
          self.button_yes.click()
        if x >= 550 and x <= 590 and y>= 430 and y<= 460 and z>= 1110 and z <= 1130 and self.obj.worker_activated and g > 50:
          self.obj.worker_activated = False
          time.sleep(0.20)
          self.button_no.click()

      @qtc.pyqtSlot()
      def yes_button_pressed(self):
        self.step_1_ui = Step_1_UI()
        self.step_1_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def no_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

class Entry_Step_2_UI(qtw.QWidget):
      def __init__(self):
        super().__init__()
        self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
        self.ui = uic.loadUi('food_assist_gui_entry_step2.ui', self)
        self.resize(1680, 1050)
        self.button_yes.clicked.connect(self.yes_button_pressed)
        self.button_no.clicked.connect(self.no_button_pressed)

      @qtc.pyqtSlot()
      def yes_button_pressed(self):
        self.step_2_ui = Step_2_UI()
        self.step_2_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def no_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

class Entry_Step_3_UI(qtw.QWidget):
      def __init__(self):
        super().__init__()
        self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
        self.ui = uic.loadUi('food_assist_gui_entry_step3.ui', self)
        self.resize(1680, 1050)
        self.button_yes.clicked.connect(self.yes_button_pressed)
        self.button_no.clicked.connect(self.no_button_pressed)

      @qtc.pyqtSlot()
      def yes_button_pressed(self):
        self.step_3_ui = Step_3_UI()
        self.step_3_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def no_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

class Entry_Step_4_UI(qtw.QWidget):
      def __init__(self):
        super().__init__()
        self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
        self.ui = uic.loadUi('food_assist_gui_entry_step4.ui', self)
        self.resize(1680, 1050)
        self.button_yes.clicked.connect(self.yes_button_pressed)
        self.button_no.clicked.connect(self.no_button_pressed)

      @qtc.pyqtSlot()
      def yes_button_pressed(self):
        self.step_4_ui = Step_4_UI()
        self.step_4_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def no_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

########## Step 1 UI class ##########
class Step_1_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_step1.ui', self)
          self.resize(1680, 1050)
          self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
          self.playlist = QtMultimedia.QMediaPlaylist()
          file = os.path.join(os.path.dirname(__file__), "video-step1.mp4")
          self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(file)))
          self.playlist.setCurrentIndex(1)
          self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
          self.player.setVideoOutput(self.ui.VideoWidget)
          self.player.setPlaylist(self.playlist)
          self.player.setMuted(True)
          self.button_next.clicked.connect(self.next_button_pressed)
          self.button_exit.clicked.connect(self.exit_button_pressed)
          self.button_video_controller.clicked.connect(self.toggle_video)
          self.player.pause()
      
      @qtc.pyqtSlot()
      def next_button_pressed(self):
        # call placing meat UI's get_current_step() to 
        # show the appropriate entry step based on the current step

        # for manual navgation, call directly respective entry step
        self.entry_step_2_ui = Entry_Step_2_UI()
        self.entry_step_2_ui.show()
        self.close()
      
      @qtc.pyqtSlot()
      def exit_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def toggle_video(self):
          if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
          else:
            self.player.play()

########## Step 2 UI class ##########
class Step_2_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_step2.ui', self)
          self.resize(1680, 1050)
          self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
          self.playlist = QtMultimedia.QMediaPlaylist()
          file = os.path.join(os.path.dirname(__file__), "video-step2.mp4")
          self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(file)))
          self.playlist.setCurrentIndex(1)
          self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
          self.player.setVideoOutput(self.ui.VideoWidget)
          self.player.setPlaylist(self.playlist)
          self.player.setMuted(True)
          self.button_next.clicked.connect(self.next_button_pressed)
          self.button_exit.clicked.connect(self.exit_button_pressed)
          self.button_video_controller.clicked.connect(self.toggle_video)
          self.player.pause()
      
      @qtc.pyqtSlot()
      def next_button_pressed(self):
        self.entry_step_3_ui = Entry_Step_3_UI()
        self.entry_step_3_ui.show()
        self.close()
      
      @qtc.pyqtSlot()
      def exit_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def toggle_video(self):
          if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
          else:
            self.player.play()

########## Step 3 UI class ##########
class Step_3_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_step3.ui', self)
          self.resize(1680, 1050)
          self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
          self.playlist = QtMultimedia.QMediaPlaylist()
          file = os.path.join(os.path.dirname(__file__), "video-step3.mp4")
          self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(file)))
          self.playlist.setCurrentIndex(1)
          self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
          self.player.setVideoOutput(self.ui.VideoWidget)
          self.player.setPlaylist(self.playlist)
          self.player.setMuted(True)
          self.button_next.clicked.connect(self.next_button_pressed)
          self.button_exit.clicked.connect(self.exit_button_pressed)
          self.button_video_controller.clicked.connect(self.toggle_video)
          self.player.pause()
      
      @qtc.pyqtSlot()
      def next_button_pressed(self):
          self.entry_step_4_ui = Entry_Step_4_UI()
          self.entry_step_4_ui.show()
          self.close()
      
      @qtc.pyqtSlot()
      def exit_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def toggle_video(self):
          if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
          else:
            self.player.play()

########## Step 4 UI class ##########
class Step_4_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_step4.ui', self)
          self.resize(1680, 1050)
          self.player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
          self.playlist = QtMultimedia.QMediaPlaylist()
          file = os.path.join(os.path.dirname(__file__), "video-step4.mp4")
          self.playlist.addMedia(QtMultimedia.QMediaContent(qtc.QUrl.fromLocalFile(file)))
          self.playlist.setCurrentIndex(1)
          self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemInLoop)
          self.player.setVideoOutput(self.ui.VideoWidget)
          self.player.setPlaylist(self.playlist)
          self.player.setMuted(True)
          self.button_next.clicked.connect(self.next_button_pressed)
          self.button_exit.clicked.connect(self.exit_button_pressed)
          self.button_video_controller.clicked.connect(self.toggle_video)
          self.player.pause()
      
      @qtc.pyqtSlot()
      def next_button_pressed(self):
        self.tutorial_ends_ui = Tutorial_Ends_UI()
        self.tutorial_ends_ui.show()
        self.close()
      
      @qtc.pyqtSlot()
      def exit_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def toggle_video(self):
          if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
          else:
            self.player.play()

########## Tutorial Ends UI class ##########
class Tutorial_Ends_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_tutorial_ends.ui', self)
          self.resize(1680, 1050)
          self.button_restart.clicked.connect(self.restart_button_pressed)
          self.button_exit.clicked.connect(self.exit_button_pressed)
      
      @qtc.pyqtSlot()
      def restart_button_pressed(self):
          self.food_assist = FoodAssist()
          self.food_assist.show()
          self.close()
      
      @qtc.pyqtSlot()
      def exit_button_pressed(self):
        self.menu_default_ui = Menu_Default_UI()
        self.menu_default_ui.show()
        self.close()


########## Menu Default UI class ##########
class Menu_Default_UI(qtw.QWidget):
      def __init__(self):
          super().__init__()
          self.setWindowFlags(qtc.Qt.CustomizeWindowHint | qtc.Qt.WindowTitleHint)
          self.ui = uic.loadUi('food_assist_gui_menu_default.ui', self)
          self.resize(1680, 1050)
          self.button_step1.clicked.connect(self.step1_button_pressed)
          self.button_step2.clicked.connect(self.step2_button_pressed)
          self.button_step3.clicked.connect(self.step3_button_pressed)
          self.button_step4.clicked.connect(self.step4_button_pressed)
          self.button_restart.clicked.connect(self.restart_button_pressed)
      
      @qtc.pyqtSlot()
      def restart_button_pressed(self):
          self.food_assist = FoodAssist()
          self.food_assist.show()
          self.close()

      @qtc.pyqtSlot()
      def step1_button_pressed(self):
        self.step_1_ui = Step_1_UI()
        self.step_1_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def step2_button_pressed(self):
        self.step_2_ui = Step_2_UI()
        self.step_2_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def step3_button_pressed(self):
        self.step_3_ui = Step_3_UI()
        self.step_3_ui.show()
        self.close()

      @qtc.pyqtSlot()
      def step4_button_pressed(self):
        self.step_4_ui = Step_4_UI()
        self.step_4_ui.show()
        self.close()

def main():

   # initiate app
   app = qtw.QApplication([])
   food_assist = FoodAssist()
   food_assist.show()
   # run the app
   sys.exit(app.exec_())
#    ex.show()
  #  sys.exit(app.exec_())
if __name__ == '__main__':
   main()