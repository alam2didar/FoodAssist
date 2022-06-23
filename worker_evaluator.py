# worker_evaluator.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

sns.set(style='whitegrid', palette='muted', font_scale=1)

class WorkerEvaluator(QObject):
    first_delay_reached = pyqtSignal()
    evaluation_result = pyqtSignal(bool)
    fig_1_name = None
    fig_2_name = None
    result_text = None

    @pyqtSlot()
    def first_delay(self):
        # slow down to adapt to UI
        time.sleep(0.2)
        self.first_delay_reached.emit()

    @pyqtSlot()
    def evaluate(self, archive_file_name, evaluation_flag):
        success_flag = False
        if evaluation_flag:
            if archive_file_name:
                try:
                    print("archive_file_name is: ", archive_file_name)
                    # load data to process
                    column_names = ['timestamp', 'step', 'sensor_type', 'result_feature']
                    df = pd.read_csv(archive_file_name, header=None, names=column_names)
                    df = df.dropna()
                    df_position = df[df['sensor_type'] == 'position']
                    df_motion = df[df['sensor_type'] == 'motion']

                    # creating image, label_new_plot_1
                    plt.figure()
                    # feature 1, 2, 3
                    df_position_feature_1 = df_position[df_position['result_feature'] == 0]
                    df_position_feature_2 = df_position[df_position['result_feature'] == 1]
                    df_position_feature_3 = df_position[df_position['result_feature'] == 2]
                    # define data
                    data = [df_position_feature_1.shape[0], df_position_feature_2.shape[0], df_position_feature_3.shape[0]]
                    labels = ['gesture 1', 'gesture 2', 'gesture 3']
                    # define Seaborn color palette to use
                    colors = sns.color_palette('pastel')[0:5]
                    # create pie chart
                    plt.title("Feature Distribution")
                    plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
                    self.fig_1_name = "records/myfig_1.png"
                    plt.savefig(self.fig_1_name)
                    # percentage
                    sum = df_position_feature_1.shape[0] + df_position_feature_2.shape[0] + df_position_feature_3.shape[0]
                    if sum != 0:
                        df_position_feature_1_ratio = df_position_feature_1.shape[0] / sum
                        print("df_position_feature_1_ratio:", df_position_feature_1_ratio)
                        df_position_feature_2_ratio = df_position_feature_2.shape[0] / sum
                        print("df_position_feature_2_ratio:", df_position_feature_2_ratio)
                        df_position_feature_3_ratio = df_position_feature_3.shape[0] / sum
                        print("df_position_feature_3_ratio:", df_position_feature_3_ratio)
                        if 0.2 < df_position_feature_1_ratio < 0.33 and 0.33 < df_position_feature_2_ratio < 0.6 and 0.2< df_position_feature_2_ratio < 0.33:
                            self.result_text = "Congratualation! Your performance are as good as the expert. Click the view button to see the details."
                        else:
                            self.result_text = "Your performance are quite different from the expert. Click the view button to see the details."
                        success_flag = True
                        print("reaching point - evaluation successful")
                    else:
                        success_flag = False
                        self.result_text = "Zero records found."
                    # creating image, label_new_plot_2
                    plt.figure()
                    df_motion_dynamic = df_motion[df_motion['result_feature'] >= 1]
                    df_motion_static = df_motion[df_motion['result_feature'] < 1]
                    # define data
                    data = [df_motion_dynamic.shape[0], df_motion_static.shape[0]]
                    labels = ['active', 'inactive']
                    # define Seaborn color palette to use
                    colors = sns.color_palette('pastel')[0:5]
                    # create pie chart
                    plt.title("Activity Percentage")
                    plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
                    self.fig_2_name = "records/myfig_2.png"
                    plt.savefig(self.fig_2_name)
                    # percentage
                    sum = df_motion_dynamic.shape[0] + df_motion_static.shape[0]
                    if sum != 0:
                        df_motion_dynamic_ratio = df_motion_dynamic.shape[0] / sum
                        print("df_motion_dynamic_ratio:", df_motion_dynamic_ratio)
                        df_motion_static_ratio = df_motion_static.shape[0] / sum
                        print("df_motion_static_ratio:", df_motion_static_ratio)
                        success_flag = True
                        print("reaching point - evaluation successful")
                    else:
                        success_flag = False
                        self.result_text = "Zero records found."
                except ValueError:
                    print(ValueError)
                    print("reaching point - error encountered")
                    success_flag = False
            else:
                print("archive_file_name is none")
                success_flag = False
        self.evaluation_result.emit(success_flag)
