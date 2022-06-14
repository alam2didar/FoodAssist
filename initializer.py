import PyQt5.QtCore as qtc
import worker_websocket
import worker_recorder
import worker_evaluator

class Initializer():
  def __init__(self):
    # define current step
    self.current_step = None

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
    self.thread_websocket.start()

    # 1 - create Worker and Thread inside the Form # no parent
    self.obj_recorder = worker_recorder.WorkerRecorder()
    self.thread_recorder = qtc.QThread()

    # 3 - Move the Worker object to the Thread object
    self.obj_recorder.moveToThread(self.thread_recorder)

    # 4 - Connect Worker Signals to the Thread slots
    self.obj_recorder.archive_finished.connect(self.obj_recorder.create_new)

    # 5 - Connect Thread started signal to Worker operational slot method
    self.thread_recorder.started.connect(self.obj_recorder.archive_old)

    # 6 - Start the thread
    self.thread_recorder.start()

  # check if message received
  def onWebsocketMessage(self, sensor_type, result_feature):
    # get current step
    if self.current_step and sensor_type and result_feature:
      self.obj_recorder.write_record(self.current_step, sensor_type, result_feature)
    else:
      print("not writing, current step: ", self.current_step, ", sensor type: ", sensor_type)
