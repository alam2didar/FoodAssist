# worker_evaluator.py
from tkinter import N
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from cv2 import fastNlMeansDenoising
from numpy import average
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

sns.set(style='whitegrid', palette='muted', font_scale=1)

class WorkerEvaluator(QObject):
    first_delay_reached = pyqtSignal()
    evaluation_result = pyqtSignal(bool, bool, str, int)

    expert_feature_1_ratio_dict = {'step_1': 0.3, 'step_2': 0.4, 'step_3': 0.3, 'step_4': 0.3}
    expert_feature_2_ratio_dict = {'step_1': 0.2, 'step_2': 0.3, 'step_3': 0.2, 'step_4': 0.4}
    expert_feature_3_ratio_dict = {'step_1': 0.4, 'step_2': 0.3, 'step_3': 0.5, 'step_4': 0.2}

    @pyqtSlot()
    def first_delay(self):
        # slow down to adapt to UI
        time.sleep(0.2)
        self.first_delay_reached.emit()

    @pyqtSlot()
    def evaluate(self, archive_file_name, evaluation_flag):
        success_flag = False
        success_flag_dict = {'step_1': False, 'step_2': False, 'step_3': False, 'step_4': False}
        qualitative_result = False
        qualitative_result_dict = {'step_1': False, 'step_2': False, 'step_3': False, 'step_4': False}
        troubled_steps = ''
        score_dict = {'step_1': 0, 'step_2': 0, 'step_3': 0, 'step_4': 0}
        score_percent = 0
        # True to be good match, False for not as good
        if evaluation_flag:
            if archive_file_name:
                print('archive_file_name is: ', archive_file_name)
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
                success_flag_dict['step_1'], qualitative_result_dict['step_1'], score_dict['step_1'] = self.process_data_frame(df_step_1, 1)
                success_flag_dict['step_2'], qualitative_result_dict['step_2'], score_dict['step_2'] = self.process_data_frame(df_step_2, 2)
                success_flag_dict['step_3'], qualitative_result_dict['step_3'], score_dict['step_3'] = self.process_data_frame(df_step_3, 3)
                success_flag_dict['step_4'], qualitative_result_dict['step_4'], score_dict['step_4'] = self.process_data_frame(df_step_4, 4)
                # aggregate success_flag from each step
                success_flag = success_flag_dict['step_1'] or success_flag_dict['step_2'] or success_flag_dict['step_3'] or success_flag_dict['step_4']
                # use qualitative_result to find out troubled_steps
                qualitative_result = qualitative_result_dict['step_1'] and qualitative_result_dict['step_2'] and qualitative_result_dict['step_3'] and qualitative_result_dict['step_4']
                if not qualitative_result:
                    false_keys = [key for key, value in qualitative_result_dict.items() if not value]
                    if len(false_keys) == 1:
                        troubled_steps = f'{false_keys[0]}'
                    elif len(false_keys) > 1:
                        troubled_steps = f'{", ".join(false_keys[:-1])} and {false_keys[-1]}'
                score_percent = int(100*(score_dict['step_1'] + score_dict['step_2'] + score_dict['step_3'] + score_dict['step_4'])/4)
            else:
                print('archive_file_name is none')
                success_flag = False
        self.evaluation_result.emit(success_flag, qualitative_result, troubled_steps, score_percent)

    @pyqtSlot()
    def process_data_frame(self, data_frame_step, step_number):
        success_flag = False
        qualitative_result = False
        score_value = 0
        df_position = None
        df_motion = None
        df_position_amount = [0, 0, 0]
        df_motion_amount = [0, 0]
        try:
            # filter position and motion
            df_position = data_frame_step[data_frame_step['sensor_type'] == 'position']
            df_motion = data_frame_step[data_frame_step['sensor_type'] == 'motion']
        except ValueError:
            print(ValueError)
            print('reaching point - error encountered filtering position and motion')
            success_flag = False
        # check df_position
        if not df_position.empty:
            # feature 1, 2, 3
            for x in range(3):
                try:
                    # define data
                    df_position_amount[x] = df_position[df_position['result_feature'] == x].shape[0]
                except ValueError:
                    print(ValueError)
                    print(f'reaching point - error encountered finding position amount: {x}')
                    success_flag = False
            labels = ['gesture 1', 'gesture 2', 'gesture 3']
            # define Seaborn color palette to use
            colors = sns.color_palette('pastel')[0:5]
            # creating image, label_new_plot_1
            plt.figure()
            # create pie chart
            plt.title('How much percent did you perform each gesture?')
            plt.pie(df_position_amount, labels = labels, colors = colors, autopct='%.0f%%')
            plt.savefig(f'records/myfig_1_step_{step_number}.png')
            # percentage
            sum = df_position_amount[0] + df_position_amount[1] + df_position_amount[2]
            if sum != 0:
                df_position_feature_1_ratio = df_position_amount[0] / sum
                print('df_position_feature_1_ratio:', df_position_feature_1_ratio)
                df_position_feature_2_ratio = df_position_amount[1] / sum
                print('df_position_feature_2_ratio:', df_position_feature_2_ratio)
                df_position_feature_3_ratio = df_position_amount[2] / sum
                print('df_position_feature_3_ratio:', df_position_feature_3_ratio)
                # calculate the difference
                diff_1 = abs(self.expert_feature_1_ratio_dict[f'step_{step_number}'] - df_position_feature_1_ratio)
                diff_2 = abs(self.expert_feature_2_ratio_dict[f'step_{step_number}'] - df_position_feature_2_ratio)
                diff_3 = abs(self.expert_feature_3_ratio_dict[f'step_{step_number}'] - df_position_feature_3_ratio)
                if diff_1 > 0.3 or diff_2 > 0.3 or diff_3 > 0.3:
                    qualitative_result = False
                    score_value = 0.6
                elif diff_1 > 0.2 or diff_2 > 0.2 or diff_3 > 0.2:
                    qualitative_result = False
                    score_value = 0.7
                elif diff_1 > 0.1 or diff_2 > 0.1 or diff_3 > 0.1:
                    qualitative_result = False
                    score_value = 0.8
                elif diff_1 <= 0.1 and diff_2 <= 0.1 and diff_3 <= 0.1:
                    qualitative_result = True
                    score_value = 0.9
                success_flag = True
            else:
                success_flag = False
        # check df_motion
        if not df_motion.empty:
            df_motion_amount[0] = df_motion[df_motion['result_feature'] >= 1].shape[0]
            df_motion_amount[1] = df_motion[df_motion['result_feature'] < 1].shape[0]
            # define data
            # data = [df_motion_dynamic.shape[0], df_motion_static.shape[0]]
            labels = ['cutting', 'not cutting']
            # define Seaborn color palette to use
            colors = sns.color_palette('pastel')[0:5]
            # creating image, label_plot_2
            plt.figure()
            # create pie chart
            plt.title('How much percent of the time were you cutting?')
            plt.pie(df_motion_amount, labels = labels, colors = colors, autopct='%.0f%%')
            plt.savefig(f'records/myfig_2_step_{step_number}.png')
            # percentage
            sum = df_motion_amount[0] + df_motion_amount[1]
            if sum != 0:
                df_motion_dynamic_ratio = df_motion_amount[0] / sum
                print('df_motion_dynamic_ratio:', df_motion_dynamic_ratio)
                df_motion_static_ratio = df_motion_amount[1] / sum
                print('df_motion_static_ratio:', df_motion_static_ratio)
                # success_flag = True
                # print('reaching point - evaluation successful')
            # else:
            #     success_flag = False
        return success_flag, qualitative_result, score_value