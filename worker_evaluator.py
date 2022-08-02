# worker_evaluator.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time

class WorkerEvaluator(QObject):
    first_delay_reached = pyqtSignal()
    # evaluation_result = pyqtSignal(bool, bool, str, int)
    evaluation_result = pyqtSignal(bool, dict, dict, list, int)

    expert_amount_dict = {
        'step_1_gesture_1': 6, 'step_1_gesture_2': 12, 'step_1_gesture_3': 2,
        'step_2_gesture_1': 6, 'step_2_gesture_2': 2, 'step_2_gesture_3': 12,
        'step_3_gesture_1': 6, 'step_3_gesture_2': 14, 'step_3_gesture_3': 0,
        'step_4_gesture_1': 4, 'step_4_gesture_2': 16, 'step_4_gesture_3': 0
    }

    expert_ratio_dict = {
        'step_1_gesture_1': 0.3, 'step_1_gesture_2': 0.6, 'step_1_gesture_3': 0.1,
        'step_2_gesture_1': 0.3, 'step_2_gesture_2': 0.1, 'step_2_gesture_3': 0.6,
        'step_3_gesture_1': 0.3, 'step_3_gesture_2': 0.7, 'step_3_gesture_3': 0,
        'step_4_gesture_1': 0.2, 'step_4_gesture_2': 0.8, 'step_4_gesture_3': 0
    }

    @pyqtSlot()
    def first_delay(self):
        # slow down to adapt to UI
        time.sleep(0.2)
        self.remove_png_files()
        self.first_delay_reached.emit()

    @pyqtSlot()
    def remove_png_files(self):
        for step_number in range(1, 5):
            for gesture_index in range(1, 4):
                fig_name = f'records/count_plot_step_{step_number}_gesture_{gesture_index}.png'
                # removing png file
                if os.path.exists(fig_name):
                    os.remove(fig_name)
                else:
                    print("png file does not exist")

    @pyqtSlot()
    def remove_csv_file(self, csv_name):
        # removing png file
        if os.path.exists(csv_name):
            os.remove(csv_name)
        else:
            print("csv file does not exist")

    @pyqtSlot()
    def evaluate(self, archive_file_name, evaluation_flag):
        success_flag = False
        success_flag_dict = {'step_1': False, 'step_2': False, 'step_3': False, 'step_4': False}
        difference_dict = {'step_1': [None, None, None], 'step_2': [None, None, None], 'step_3': [None, None, None], 'step_4': [None, None, None]}
        # qualitative_result = False
        # qualitative_result_dict = {'step 1': False, 'step 2': False, 'step 3': False, 'step 4': False}
        # troubled_steps = [-1, -1, -1]
        score_dict = {'step_1': 0, 'step_2': 0, 'step_3': 0, 'step_4': 0}
        score_sorted_list = None
        score_percent = 0
        # True to be good match, False for not as good
        if evaluation_flag:
            if archive_file_name:
                print('archive_file_name is: ', archive_file_name)
                # load data to process
                column_names = ['role', 'timestamp', 'step', 'sensor_type', 'recognized_gesture']
                df_newbie = pd.read_csv(archive_file_name, header=None, names=column_names)
                df_newbie = df_newbie.dropna()
                df_expert = pd.read_csv('records/record_expert.csv', header=None, names=column_names)
                df_expert = df_expert.dropna()
                # filter data frame for each step
                df_expert_step_1 = df_expert[df_expert['step'] == 'step_1']
                df_expert_step_2 = df_expert[df_expert['step'] == 'step_2']
                df_expert_step_3 = df_expert[df_expert['step'] == 'step_3']
                df_expert_step_4 = df_expert[df_expert['step'] == 'step_4']
                df_newbie_step_1 = df_newbie[df_newbie['step'] == 'step_1']
                df_newbie_step_2 = df_newbie[df_newbie['step'] == 'step_2']
                df_newbie_step_3 = df_newbie[df_newbie['step'] == 'step_3']
                df_newbie_step_4 = df_newbie[df_newbie['step'] == 'step_4']
                # perform the same data processing on each step dataset
                success_flag_dict['step_1'], difference_dict['step_1'], score_dict['step_1'] = self.process_data_frame(df_expert_step_1, df_newbie_step_1, 1)
                success_flag_dict['step_2'], difference_dict['step_2'], score_dict['step_2'] = self.process_data_frame(df_expert_step_2, df_newbie_step_2, 2)
                success_flag_dict['step_3'], difference_dict['step_3'], score_dict['step_3'] = self.process_data_frame(df_expert_step_3, df_newbie_step_3, 3)
                success_flag_dict['step_4'], difference_dict['step_4'], score_dict['step_4'] = self.process_data_frame(df_expert_step_4, df_newbie_step_4, 4)
                # aggregate success_flag from each step
                success_flag = success_flag_dict['step_1'] or success_flag_dict['step_2'] or success_flag_dict['step_3'] or success_flag_dict['step_4']
                # use score_value to find out the ranking - to do
                score_sorted_list = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
                # use qualitative_result to find out troubled_steps
                # qualitative_result = qualitative_result_dict['step 1'] and qualitative_result_dict['step 2'] and qualitative_result_dict['step 3'] and qualitative_result_dict['step 4']
                # if not qualitative_result:
                #     false_keys = [key for key, value in qualitative_result_dict.items() if not value]
                #     if len(false_keys) == 1:
                #         troubled_steps = f'{false_keys[0]}'
                #     elif len(false_keys) > 1:
                #         troubled_steps = f'{", ".join(false_keys[:-1])} and {false_keys[-1]}'
                score_percent = int((score_dict['step_1'] + score_dict['step_2'] + score_dict['step_3'] + score_dict['step_4'])/4)
            else:
                print('archive_file_name is none')
                success_flag = False
        # self.evaluation_result.emit(success_flag, qualitative_result, troubled_steps, score_percent)
        self.evaluation_result.emit(success_flag, difference_dict, score_dict, score_sorted_list, score_percent)

    @pyqtSlot()
    def process_data_frame(self, data_frame_expert_step, data_frame_newbie_step, step_number):
        success_flag = False
        # qualitative_result = False
        score_value = 0
        df_position = None
        # df_motion = None
        df_newbie_position_amount = [0, 0, 0]
        amount_difference = [None, None, None]
        # gesture_ratio = [0, 0, 0]
        # ratio_difference = [0, 0, 0]
        # df_motion_amount = [0, 0]
        try:
            # filter position and motion
            df_expert_position = data_frame_expert_step[data_frame_expert_step['sensor_type'] == 'position']
            df_newbie_position = data_frame_newbie_step[data_frame_newbie_step['sensor_type'] == 'position']
            df_position = df_expert_position.append(df_newbie_position)
            # df_newbie_motion = data_frame_newbie_step[data_frame_newbie_step['sensor_type'] == 'motion']
        except ValueError:
            print(ValueError)
            print('reaching point - error encountered filtering position and motion')
            success_flag = False
        # check df_position
        # if not df_newbie_position.empty:
        for gesture_index in range(1, 4):
            # filter gesture x
            df_position_gesture_x = df_position[df_position['recognized_gesture'] == gesture_index]
            try:
                # define data
                df_newbie_position_amount[gesture_index-1] = df_position_gesture_x.shape[0]
            except ValueError:
                print(ValueError)
                print(f'reaching point - error encountered finding position amount: {gesture_index}')
                success_flag = False
            # define Seaborn color palette to use
            sns.set(style='whitegrid', palette='muted', font_scale=1)
            # creating image - gesture x - change plot size
            # plt.figure(figsize=(12, 4.8)).gca().yaxis.get_major_locator().set_params(integer=True)
            plt.figure(figsize=(12, 4.8))
            # count plot
            # plt.title('How many times did you perform each gesture?')
            # plt.title('How many times does an expert perform each gesture?')
            sns_count_plot = sns.countplot(y='role', data=df_position_gesture_x, order=['expert', 'newbie'])
            strFile = f'records/count_plot_step_{step_number}_gesture_{gesture_index}.png'
            if os.path.isfile(strFile):
                os.remove(strFile)
            sns_count_plot.figure.savefig(strFile)

            # labels = ['gesture 1', 'gesture 2', 'gesture 3']
            # # creating percentage image
            # plt.figure()
            # # pie chart
            # plt.title('Ratio of each gesture performed by you:')
            # # plt.title('Ratio of each gesture performed by an expert:')
            # # define Seaborn color palette to use
            # colors = sns.color_palette('pastel')[0:5]
            # sns.set(style='whitegrid', palette='muted', font_scale=1)
            # plt.pie(df_newbie_position_amount, labels = labels, colors = colors, autopct='%.0f%%')
            # plt.savefig(f'records/plot_2_user_step_{step_number}.png')
            # percentage
            sum = df_newbie_position_amount[0] + df_newbie_position_amount[1] + df_newbie_position_amount[2]
            if sum != 0:
                for gesture_index in range(1, 4):
                    amount_difference[gesture_index-1] = df_newbie_position_amount[gesture_index-1] - self.expert_amount_dict[f'step_{step_number}_gesture_{gesture_index}']
                # calculation of score_value
                if abs(amount_difference[0]) > 4 or abs(amount_difference[1]) > 4 or abs(amount_difference[2]) > 4:
                    # qualitative_result = False
                    score_value = 60
                elif abs(amount_difference[0]) > 3 or abs(amount_difference[1]) > 3 or abs(amount_difference[2]) > 3:
                    # qualitative_result = False
                    score_value = 70
                elif abs(amount_difference[0]) > 2 or abs(amount_difference[1]) > 2 or abs(amount_difference[2]) > 2:
                    # qualitative_result = True
                    score_value = 80
                elif abs(amount_difference[0]) > 1 or abs(amount_difference[1]) > 1 or abs(amount_difference[2]) > 1:
                    # qualitative_result = True
                    score_value = 90
                # elif amount_difference == [0, 0, 0]:
                #     # qualitative_result = True
                #     score_value = 100
                elif amount_difference == [None, None, None]:
                    score_value = 0
                success_flag = True
            else:
                success_flag = False
        # check df_motion
        # if not df_motion.empty:
        #     df_motion_amount[0] = df_motion[df_motion['result_gesture'] >= 1].shape[0]
        #     df_motion_amount[1] = df_motion[df_motion['result_gesture'] < 1].shape[0]
        #     # define data
        #     # data = [df_motion_dynamic.shape[0], df_motion_static.shape[0]]
        #     labels = ['cutting', 'not cutting']
        #     # define Seaborn color palette to use
        #     colors = sns.color_palette('pastel')[0:5]
        #     # creating image, label_plot_2
        #     plt.figure()
        #     # create pie chart
        #     plt.title('How much percent of the time were you cutting?')
        #     plt.pie(df_motion_amount, labels = labels, colors = colors, autopct='%.0f%%')
        #     plt.savefig(f'records/myfig_0_step_{step_number}.png')
        # return success_flag, qualitative_result, score_value
        return success_flag, amount_difference, score_value