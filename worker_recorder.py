# worker_recorder.py
import os
import datetime
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class WorkerRecorder(QObject):
    archive_finished = pyqtSignal()
    permission_to_write = False

    current_csv_name = "records/record_current.csv"
    current_fig_1_name = "records/myfig_1.png"
    current_fig_2_name = "records/myfig_2.png"
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
        if self.file_writer:
            self.file_writer.close()
            self.file_writer = None

    @pyqtSlot()
    def archive_old(self):
        archive_csv_name = None
        archive_fig_1_name = None
        archive_fig_2_name = None
        self.disable_writing()
        # close file writer before archiving
        self.close_file()
        try:
            # archive - renaming file
            archive_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            archive_csv_name = "records/record_{}.csv".format(archive_time)
            os.rename(self.current_csv_name, archive_csv_name)
            print("archived successfully")
            # send signal to create new
            self.archive_finished.emit()
        except FileNotFoundError:
            print("warning - csv file not found")
            archive_csv_name = None
            # send signal to create new
            self.archive_finished.emit()
        try:
            # archive - renaming file
            archive_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
            archive_fig_1_name = "records/myfig_1_{}.png".format(archive_time)
            archive_fig_2_name = "records/myfig_2_{}.png".format(archive_time)
            os.rename(self.current_fig_1_name, archive_fig_1_name)
            os.rename(self.current_fig_2_name, archive_fig_2_name)
            print("archived png successfully")
        except FileNotFoundError:
            print("warning - png file not found")
            archive_fig_1_name = None
            archive_fig_2_name = None
        # csv name required
        return archive_csv_name

    @pyqtSlot()
    def create_new(self):
        if not self.permission_to_write and not self.file_writer:
            os.makedirs("./records", exist_ok=True)
            # new file writer
            self.file_writer = open(self.current_csv_name, "w")
            print("open file writer successfully")

    @pyqtSlot()
    def write_record(self, current_step, sensor_type, result_feature):
        if self.permission_to_write and self.file_writer:
            # get current time
            current_time = datetime.datetime.now()
            current_time_s = current_time.strftime("%y%m%d%H%M%S")
            current_time_ms = "{:06d}".format(current_time.microsecond)
            # write into csv file
            self.file_writer.write("{}{},step_{},{},{}\n".format(current_time_s, current_time_ms, current_step, sensor_type, result_feature))
        else:
            print("no permission to write")
