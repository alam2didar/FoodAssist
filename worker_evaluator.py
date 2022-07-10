# worker_evaluator.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

sns.set(style='whitegrid', palette='muted', font_scale=1)

class WorkerEvaluator(QObject):
    first_delay_reached = pyqtSignal()
    evaluation_result = pyqtSignal(bool, bool, str)

    @pyqtSlot()
    def first_delay(self):
        # slow down to adapt to UI
        time.sleep(0.2)
        self.first_delay_reached.emit()

    @pyqtSlot()
    def evaluate(self, archive_file_name, evaluation_flag):
        success_flag = False
        success_flag_dict = {"step_1": False, "step_2": False, "step_3": False, "step_4": False}
        qualitative_result = False
        qualitative_result_dict = {"step_1": False, "step_2": False, "step_3": False, "step_4": False}
        troubled_steps = None
        # True to be good match, False for not as good
        if evaluation_flag:
            if archive_file_name:
                print("archive_file_name is: ", archive_file_name)
                # load data to process
                column_names = ['timestamp', 'step', 'sensor_type', 'result_feature']
                df = pd.read_csv(archive_file_name, header=None, names=column_names)
                df = df.dropna()
                # filter data frame for each step
                df_step_1 = df[df['step'] == 'step_1']
                df_step_2 = df[df['step'] == 'step_2']
                df_step_3 = df[df['step'] == 'step_3']
                df_step_4 = df[df['step'] == 'step_4']
                # perform the same data processing on each step dataset
                success_flag_dict['step_1'], qualitative_result_dict['step_1'] = self.process_data_frame(df_step_1, 1)
                success_flag_dict['step_2'], qualitative_result_dict['step_2'] = self.process_data_frame(df_step_2, 2)
                success_flag_dict['step_3'], qualitative_result_dict['step_3'] = self.process_data_frame(df_step_3, 3)
                success_flag_dict['step_4'], qualitative_result_dict['step_4'] = self.process_data_frame(df_step_4, 4)
                # aggregate success_flag from each step
                success_flag = success_flag_dict['step_1'] or success_flag_dict['step_2'] or success_flag_dict['step_3'] or success_flag_dict['step_4']
                # use qualitative_result to find out troubled_steps
                qualitative_result = qualitative_result_dict['step_1'] and qualitative_result_dict['step_2'] and qualitative_result_dict['step_3'] and qualitative_result_dict['step_4']
                if not qualitative_result:
                    false_keys = [key for key, value in qualitative_result_dict.items() if not value]
                    if len(false_keys) == 1:
                        troubled_steps = f"{false_keys[0]}"
                    elif len(false_keys) > 1:
                        troubled_steps = f"{', '.join(false_keys[:-1])} and {false_keys[-1]}"
            else:
                print("archive_file_name is none")
                success_flag = False
        self.evaluation_result.emit(success_flag, qualitative_result, troubled_steps)

    @pyqtSlot()
    def process_data_frame(self, data_frame_step, step_number):
        success_flag = False
        qualitative_result = False
        try:
            df_position = data_frame_step[data_frame_step['sensor_type'] == 'position']
            df_motion = data_frame_step[data_frame_step['sensor_type'] == 'motion']

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
            plt.title("How much percent did you perform each gesture?")
            plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
            plt.savefig(f"records/myfig_1_step_{step_number}.png")
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
                    qualitative_result = True
                else:
                    qualitative_result = False
                success_flag = True
            else:
                success_flag = False
            # creating image, label_plot_2
            plt.figure()
            df_motion_dynamic = df_motion[df_motion['result_feature'] >= 1]
            df_motion_static = df_motion[df_motion['result_feature'] < 1]
            # define data
            data = [df_motion_dynamic.shape[0], df_motion_static.shape[0]]
            labels = ['cutting', 'not cutting']
            # define Seaborn color palette to use
            colors = sns.color_palette('pastel')[0:5]
            # create pie chart
            plt.title("How much percent of the time were you cutting?")
            plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
            plt.savefig(f"records/myfig_2_step_{step_number}.png")
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
        except ValueError:
            print(ValueError)
            print("reaching point - error encountered")
            success_flag = False
        return success_flag, qualitative_result