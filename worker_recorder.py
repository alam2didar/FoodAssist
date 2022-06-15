# worker_recorder.py
import os
import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class WorkerRecorder(QObject):
    archive_finished = pyqtSignal()
    permission_to_write = False
    current_file_name = "record_current.csv"
    file_writer = None

    @pyqtSlot()
    def enable_writing(self):
        if not self.permission_to_write:
            self.permission_to_write = True
            print("enabled writing successfully")

    @pyqtSlot()
    def disable_writing(self):
        if self.permission_to_write:
            self.permission_to_write = False
            print("disabled writing successfully")

    @pyqtSlot()
    def close_file(self):
        # close file writer
        self.file_writer.close()

    @pyqtSlot()
    def archive_old(self):
        archive_file_name = None
        self.disable_writing()
        # close file writer before archiving
        if self.file_writer is not None:
            self.file_writer.close()
        try:
            # archive - renaming file
            archive_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            archive_file_name = "record_{}.csv".format(archive_time)
            os.rename(self.current_file_name, archive_file_name)
            print("archived successfully")
            # send signal to create new
            self.archive_finished.emit()
        except FileNotFoundError:
            print("warning - file not found")
            # send signal to create new
            self.archive_finished.emit()
        return archive_file_name

    @pyqtSlot()
    def create_new(self):
        if not self.permission_to_write:
            # new file writer
            self.file_writer = open(self.current_file_name, "w")
            print("open file writer successfully")

    @pyqtSlot()
    def write_record(self, current_step, sensor_type, result_feature):
        if self.permission_to_write:
            # get current time
            current_time = datetime.datetime.now()
            current_time_s = current_time.strftime("%y%m%d%H%M%S")
            current_time_ms = "{:06d}".format(current_time.microsecond)
            # write into csv file
            self.file_writer.write("{}{},step_{},{},{}\n".format(current_time_s, current_time_ms, current_step, sensor_type, result_feature))
            print("writing record...")
        else:
            print("no permission to write")
