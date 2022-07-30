import PyQt5.QtCore as qtc
import DepthCameraModule as dcm
from foodAssist import Placing_Meat_UI
import worker_websocket
import worker_recorder
import worker_detection

class Initializer(qtc.QObject):
  detectionParams = qtc.pyqtSignal(int, int, int, int, int)
  # flag to start/block workers
  # start_worker = False
  start_worker = True
  interval_between_uis = 20

  def __init__(self, last_class=Placing_Meat_UI):
    super().__init__()
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

    # Initialize Depth Camera Intel Realsense
    #####
    # comment for no camera device
    self.my_depth_camera = dcm.DepthCamera()
    # self.my_depth_camera = None
    #####

    # Create WorkerWebsocket thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_websocket = worker_websocket.WorkerWebsocket()
    self.thread_websocket = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    self.obj_websocket.websocket_message.connect(self.onWebsocketMessage)
    # 3 - Move the Worker object to the Thread object
    self.obj_websocket.moveToThread(self.thread_websocket)
    # 4 - Connect Worker Signals to the Thread slots
    self.obj_websocket.websocket_finished.connect(self.thread_websocket.quit)
    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_websocket.started.connect(self.obj_websocket.create_websocket)
    # 6 - Start the thread
    if self.start_worker:
      self.thread_websocket.start()

    # Create WorkerRecorder thread
    self.obj_recorder = worker_recorder.WorkerRecorder()
    self.thread_recorder = qtc.QThread()
    self.obj_recorder.moveToThread(self.thread_recorder)
    self.obj_recorder.archive_finished.connect(self.obj_recorder.create_new)
    self.thread_recorder.started.connect(self.obj_recorder.archive_old)
    if self.start_worker:
      self.thread_recorder.start()
    
    # Create WorkerDetection thread
    self.obj_detection = worker_detection.WorkerDetection(self.my_depth_camera)
    self.thread_detection = qtc.QThread()
    self.obj_detection.detectionParams.connect(self.onDetection)
    self.obj_detection.moveToThread(self.thread_detection)
    self.obj_detection.finished.connect(self.thread_detection.quit)
    self.thread_detection.started.connect(self.obj_detection.detectStep)
    if self.start_worker:
      self.thread_detection.start()

  # check if message received
  def onWebsocketMessage(self, sensor_type, message):
    # get current step
    if self.current_step:
      self.obj_recorder.write_record(self.current_step, sensor_type, message)
      print("writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)
    else:
      print("not writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)

  # send detection box paramas to the respective UI  
  def onDetection(self, x, y, width, height, step):
      self.detected_step = step
      # calibrate x,y,w,h for projection with k=1.65 and (x,y) = (405,220)
      if x == 0 or y == 0:
        self.detectionParams.emit(0,0,0,0,0)
      else:
        self.detectionParams.emit(int(1.65*(x-405)), int(1.65*(y-220)), int(1.65*width), int(1.65*height), step)
        
