# worker_evaluator.py
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import pandas as pd
import seaborn as sns

sns.set(style='whitegrid', palette='muted', font_scale=1)

class WorkerEvaluator(QObject):

    evaluation_finished = False
    fig_1_name = None
    fig_2_name = None
    result_text = None

    @pyqtSlot()
    def evaluate(self, archive_file_name, evaluation_flag):
        if evaluation_flag:
            if archive_file_name is None:
                print("archive_file_name is None")
            else:
                try:
                    print("archive_file_name is: ", archive_file_name)
                    # load data to process
                    column_names = ['timestamp', 'step', 'sensor_type', 'result_feature']
                    df = pd.read_csv(archive_file_name, header=None, names=column_names)
                    df = df.dropna()
                    df_position = df[df['sensor_type'] == 'position']
                    df_motion = df[df['sensor_type'] == 'motion']
                    # creating image, label_new_plot_3
                    new_plot_1 = sns.countplot(x = 'step',
                            hue = 'result_feature',
                            data = df_position,
                            order = df_position.step.value_counts().index);
                    self.fig_1_name = "myfig_1.png"
                    new_plot_1.figure.savefig(self.fig_1_name)
                    # creating image, label_new_plot_3
                    new_plot_2 = sns.countplot(x = 'step',
                            hue = 'result_feature',
                            data = df_motion,
                            order = df_motion.step.value_counts().index);
                    self.fig_2_name = "myfig_2.png"
                    new_plot_2.figure.savefig(self.fig_2_name)
                    # process for result text, label_new_plot_3
                    df_position_step_1 = df_position[df_position['step'] == 'step_1']
                    df_position_step_1_feature_1 = df_position_step_1[df_position_step_1['result_feature'] == 1]
                    df_position_step_1_feature_2 = df_position_step_1[df_position_step_1['result_feature'] == 2]
                    df_position_step_1_feature_3 = df_position_step_1[df_position_step_1['result_feature'] == 3]
                    sum = df_position_step_1_feature_1.shape[0] + df_position_step_1_feature_2.shape[0] + df_position_step_1_feature_3.shape[0]
                    result_ratio = df_position_step_1_feature_1.shape[0] / sum
                    print("result_ratio:", result_ratio)
                    # to do - define expert range?
                    if result_ratio >= 0.6 and result_ratio <= 1:
                        self.result_text = "In step 1, you have been scoring the chopping gesture (picture 1) more frequently than the expert."
                    elif result_ratio > 0.4 and result_ratio < 0.6:
                        self.result_text = "In step 1, you have been scoring the chopping gesture (picture 1) as frequently as the expert."
                    elif result_ratio >= 0 and result_ratio <= 0.4:
                        self.result_text = "In step 1, you have been scoring the chopping gesture (picture 1) less frequently than the expert."
                    # set evaluation finished flag
                    self.evaluation_finished = True
                    print("reaching point - evaluation finished")
                except ValueError:
                    print(ValueError)
                    print("reaching point - error encountered")
