import PyQt5.QtCore as qtc
import worker_websocket
import worker_recorder
import worker_udp
import worker_evaluator

class Initializer(qtc.QObject):
  devices_connected = qtc.pyqtSignal()
  devices_disconnected = qtc.pyqtSignal()
  # flag to start/block workers
  # start_worker = False
  start_worker = True
  interval_between_uis = 20

  def __init__(self):
    super().__init__()
    # define list of gestures
    self.gesture_id_list = ["s1g1", "s1g2", "s1g3", "s2g1", "s3g1", "s3g2", "s3g3", "s3g4", "s4g1", "s4g2"]

    # initial status of devices
    self.devices_running = False
    # define current step
    self.current_step = None

    # Create WorkerUdp thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_udp = worker_udp.WorkerUdp()
    self.thread_udp = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    self.obj_udp.current_step_update.connect(self.set_current_step)
    self.obj_udp.result_requested.connect(self.retrieve_result)
    # 3 - Move the Worker object to the Thread object
    self.obj_udp.moveToThread(self.thread_udp)
    # 4 - Connect Worker Signals to the Thread slots
    self.obj_udp.udp_finished.connect(self.thread_udp.quit)
    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_udp.started.connect(self.obj_udp.receive_message)
    # 6 - Start the thread
    if self.start_worker:
      self.thread_udp.start()
    print("worker udp is up")

    # Create WorkerWebsocket thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_websocket = worker_websocket.WorkerWebsocket()
    self.thread_websocket = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    self.obj_websocket.websocket_message.connect(self.onWebsocketMessage)
    self.obj_websocket.phone_and_watch_start.connect(self.onDeviceStart)
    self.obj_websocket.phone_and_watch_stop.connect(self.onDeviceStop)
    # 3 - Move the Worker object to the Thread object
    self.obj_websocket.moveToThread(self.thread_websocket)
    # 4 - Connect Worker Signals to the Thread slots
    self.obj_websocket.websocket_finished.connect(self.thread_websocket.quit)
    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_websocket.started.connect(self.obj_websocket.create_websocket)
    # 6 - Start the thread
    if self.start_worker:
      self.thread_websocket.start()
    print("worker websocket is up")

    # Create WorkerRecorder thread
    self.obj_recorder = worker_recorder.WorkerRecorder()
    self.thread_recorder = qtc.QThread()
    self.obj_recorder.moveToThread(self.thread_recorder)
    self.obj_recorder.archive_finished.connect(self.obj_recorder.create_new)
    self.thread_recorder.started.connect(self.obj_recorder.archive_old)
    if self.start_worker:
      self.thread_recorder.start()
    print("worker recorder is up")

    # Create WorkerEvaluator thread
    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_evaluator = worker_evaluator.WorkerEvaluator()
    self.thread_evaluator = qtc.QThread()
    # 2 - Connect Worker`s Signals to Form method slots to post data.
    self.obj_evaluator.first_delay_reached.connect(self.onFirstDelayReached)
    self.obj_evaluator.evaluation_result.connect(self.onEvaluationResult)
    # 3 - Move the Worker object to the Thread object
    self.obj_evaluator.moveToThread(self.thread_evaluator)
    # 5 - Connect Thread started signal to Worker operational slot method
    # self.thread_evaluator.started.connect(self.obj_evaluator.first_delay)
    # * - Thread finished signal will close the app (if needed!)
    # self.thread.finished.connect(app.exit)
    # 6 - Start the thread
    self.thread_evaluator.start()
    print("worker evaluator is up")

  def set_current_step(self, stage):
    if stage == -1:
      self.current_step = None
    elif stage == 0:
      self.current_step = None
      # stop recording
      # self.obj_recorder.disable_writing()
      # close file
      self.obj_recorder.close_file()
      # archiving csv file - followed by creating new csv file
      self.archive_csv_name = self.obj_recorder.archive_old()
      # start recording
      # self.obj_recorder.enable_writing()
      # prepare for evaluation
      print("preparing for evaluation")
      self.obj_evaluator.first_delay()
    else:
      # set current step
      self.current_step = stage
      print(f"reaching at stage {self.current_step}")

  def retrieve_result(self, request_id):
    if request_id in self.gesture_id_list:
      print("request_id " + request_id + " in the list")
      if self.success_flag == True:
        print("evalution was successful")
        response_id = request_id
        gesture_score = self.get_gesture_score(request_id)
        self.obj_udp.send_message(-1, response_id, gesture_score)
        print("send back result")
      else:
        print("evalution wasn't successful")
    else:
      print("request_id " + request_id + " not in the list")

  def get_gesture_score(self, request_id):
    step_number = int(request_id[1])
    gesture_number = int(request_id[3])
    gesture_score = self.score_dict[f'step_{step_number}'][gesture_number-1]
    print(f"looking up step {step_number} gesture {gesture_number}")
    return gesture_score

  def onFirstDelayReached(self):
      print("first delay reached")
      # debug - setting evaluation_flag to True
      self.obj_evaluator.evaluate(self.archive_csv_name, True)

  def onEvaluationResult(self, success_flag, difference_dict, score_dict, step_score_dict, step_score_sorted_list, overall_score_percentage):
    # save evaluation result in my_initializer
    self.success_flag = success_flag
    self.difference_dict = difference_dict
    self.score_dict = score_dict
    self.step_score_dict = step_score_dict
    self.step_score_sorted_list = step_score_sorted_list
    self.overall_score_percentage = overall_score_percentage
    print("retrived evaluation result")
    if self.success_flag:
      # to do - send error code 0 to worker udp
      self.obj_udp.send_message(0, "-1", -1)
    else:
      # to do - send error code 1 to worker udp
      self.obj_udp.send_message(1, "-1", -1)

  # check if message received
  def onWebsocketMessage(self, sensor_type, message):
    # get current step
    if self.current_step:
      self.obj_recorder.write_record(self.current_step, sensor_type, message)
      print("writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)
    else:
      print("not writing, current step: ", self.current_step, ", sensor type: ", sensor_type, ", message: ", message)

  def onDeviceStart(self):
    print("mobile devices are running")
    self.devices_running = True
    self.devices_connected.emit()

  def onDeviceStop(self):
    print("mobile devices not running")
    self.devices_running = False
    self.devices_disconnected.emit()
