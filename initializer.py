import PyQt5.QtCore as qtc
import DepthCameraModule as dcm
from foodAssist import Placing_Meat_UI
import worker_websocket
import worker_recorder
import worker_detection
import worker_handpos
import worker_evaluator
import copy
import numpy as np


class Initializer(qtc.QObject):
  hand_position = qtc.pyqtSignal(int, int, int, int, int, int)
  gesture_to_ui = qtc.pyqtSignal(int)
  detection_params = qtc.pyqtSignal(int, int, int, int, int)
  devices_connected = qtc.pyqtSignal()
  devices_disconnected = qtc.pyqtSignal()
  # debug_mode to start/block workers
  debug_mode = False
  interval_between_uis = 15

  def __init__(self, last_class=Placing_Meat_UI):
    super().__init__()
    # initial status of devices
    self.devices_running = False
    # define current step
    self.current_step = None
    # detected step (by detection model)
    self.detected_step = 0
    # last class which has called the current class
    self.last_class = last_class
    # users' language (default is English: en)
    self.lang = 'en'
    # users' knife hand (default is right)
    self.knife_hand = 'right'

    # Create vision-based probabilities array
    #####
    self.vision_prob_array = []
    #####

    # Initialize Depth Camera Intel Realsense
    #####
    # comment for no camera device
    if self.debug_mode:
      self.my_depth_camera = None
    else:
      self.my_depth_camera = dcm.DepthCamera()
    #####

    # Create WorkerHandPos thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj = worker_handpos.WorkerHandPos(self.my_depth_camera)
    self.obj.vision_based_prob_message.connect(self.onVisionBasedProbs)
    self.thread_handpos = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    self.obj.hand_position.connect(self.onHandPosition)
    # 3 - Move the Worker object to the Thread object
    self.obj.moveToThread(self.thread_handpos)
    # 4 - Connect Worker Signals to the Thread slots
    self.obj.finished.connect(self.thread_handpos.quit)
    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_handpos.started.connect(self.obj.get_hand_position)
    # 6 - Start the thread
    if not self.debug_mode:
      self.thread_handpos.start()

    # Create WorkerWebsocket thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_websocket = worker_websocket.WorkerWebsocket()
    self.thread_websocket = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    # self.obj_websocket.websocket_message.connect(self.onWebsocketMessage)
    # replace with directly emitted probabilities
    self.obj_websocket.sensor_based_prob_message.connect(self.onSensorBasedProbs)
    self.obj_websocket.phone_and_watch_start.connect(self.onDeviceStart)
    self.obj_websocket.phone_and_watch_stop.connect(self.onDeviceStop)
    # 3 - Move the Worker object to the Thread object
    self.obj_websocket.moveToThread(self.thread_websocket)
    # 4 - Connect Worker Signals to the Thread slots
    self.obj_websocket.websocket_finished.connect(self.thread_websocket.quit)
    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_websocket.started.connect(self.obj_websocket.create_websocket)
    # 6 - Start the thread
    if not self.debug_mode:
      self.thread_websocket.start()

    # Create WorkerRecorder thread
    self.obj_recorder = worker_recorder.WorkerRecorder()
    self.thread_recorder = qtc.QThread()
    self.obj_recorder.moveToThread(self.thread_recorder)
    self.obj_recorder.archive_finished.connect(self.obj_recorder.create_new)
    self.thread_recorder.started.connect(self.obj_recorder.archive_old)
    self.thread_recorder.start()
    
    # Create WorkerDetection thread
    self.obj_detection = worker_detection.WorkerDetection(self.my_depth_camera)
    self.thread_detection = qtc.QThread()
    self.obj_detection.detection_params.connect(self.onDetection)
    self.obj_detection.moveToThread(self.thread_detection)
    self.obj_detection.finished.connect(self.thread_detection.quit)
    self.thread_detection.started.connect(self.obj_detection.detect_step)
    if not self.debug_mode:
      self.thread_detection.start()

    # Create WorkerEvaluator thread
    self.obj_evaluator = worker_evaluator.WorkerEvaluator()
    self.thread_evaluator = qtc.QThread()
    self.obj_evaluator.moveToThread(self.thread_evaluator)
    self.thread_evaluator.start()

  def onVisionBasedProbs(self, sensor_type, prob_0, prob_1, prob_2, prob_3):
    vision_probs = [prob_0, prob_1, prob_2, prob_3]
    self.vision_prob_array.append(vision_probs)

  def onSensorBasedProbs(self, sensor_type, prob_0, prob_1, prob_2, prob_3):
    # put sensor based probabilities into array
    sensor_probs = [prob_0, prob_1, prob_2, prob_3]
    if len(self.vision_prob_array) == 0:
      # in case no vision based probabilities
      fused_probs = sensor_probs
    else:
      # retrieve from container of vision based probabilities
      temp_vision_prob_array = copy.deepcopy(self.vision_prob_array)
      # clear container of vision based probabilities
      self.vision_prob_array.clear()
      # get mean values
      vision_probs = np.mean(temp_vision_prob_array, axis=0)
      # fuse vision and sensor based probabilities
      fused_probs = np.mean([sensor_probs, vision_probs], axis=0)
    # pick out the biggest number in an array
    if np.max(fused_probs) > 0.5:
      # get the index number of the biggest number in an array and plus 1 to get feature index
      result_gesture = np.argmax(fused_probs) + 1
      # debug
      self.gesture_to_ui.emit(result_gesture)
      # get current step
      if self.current_step:
        sensor_type = 'fused'
        self.obj_recorder.write_record(self.current_step, sensor_type, result_gesture)
        print("writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", result_gesture)
      else:
        print("not writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", result_gesture)

  # # check if message received
  # def onWebsocketMessage(self, sensor_type, message):
  #   # get current step
  #   if self.current_step:
  #     self.obj_recorder.write_record(self.current_step, sensor_type, message)
  #     print("writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)
  #   else:
  #     print("not writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)

  # send hand position paramas to the respective UI  
  def onHandPosition(self, x, y, z, counter, cursor_x, cursor_y):
    self.hand_position.emit(x, y, z, counter, cursor_x, cursor_y)

  # send detection box paramas to the respective UI  
  def onDetection(self, x, y, width, height, step):
      self.detected_step = step
      # calibrate x,y,w,h for projection with k=1.65 and (x,y) = (405,220)
      if x == 0 or y == 0:
        self.detection_params.emit(0,0,0,0,0)
      else:
        self.detection_params.emit(int(1.65*(x-405)), int(1.65*(y-220)), int(1.65*width), int(1.65*height), step)

  def onDeviceStart(self):
    self.devices_running = True
    self.devices_connected.emit()

  def onDeviceStop(self):
    self.devices_running = False
    self.devices_disconnected.emit()
