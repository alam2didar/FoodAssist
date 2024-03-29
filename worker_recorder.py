# worker_recorder.py
import os
import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class WorkerRecorder(QObject):
    archive_finished = pyqtSignal()
    # permission_to_write = False

    current_csv_name = "records/record_current.csv"
    archive_csv_name = "records/record_archived.csv"
    file_writer = None

    @pyqtSlot()
    def close_file(self):
        # close file writer
        if self.file_writer:
            self.file_writer.close()
            self.file_writer = None

    @pyqtSlot()
    def archive_old(self):
        archive_csv_name = None
        # close file writer before archiving
        self.close_file()
        if os.path.exists(self.current_csv_name):
            # archive - renaming csv file
            archive_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            archive_csv_name = "records/record_{}.csv".format(archive_time)
            os.rename(self.current_csv_name, archive_csv_name)
            print("archived successfully")
        else:
            print("csv file does not exist")
        self.archive_finished.emit()
        return archive_csv_name

    @pyqtSlot()
    def create_new(self):
        if not self.file_writer:
            os.makedirs("./records", exist_ok=True)
            # new file writer
            self.file_writer = open(self.current_csv_name, "w")
            print("open file writer successfully")

    @pyqtSlot()
    def write_record(self, current_step, sensor_type, result_gesture):
        if self.file_writer:
            # get current time
            current_time = datetime.datetime.now()
            current_time_s = current_time.strftime("%y%m%d%H%M%S")
            current_time_ms = "{:06d}".format(current_time.microsecond)
            # write into csv file - for newbie
            self.file_writer.write("newbie,{}{},step_{},{},{}\n".format(current_time_s, current_time_ms, current_step, sensor_type, result_gesture))
        else:
            print("no permission to write")
