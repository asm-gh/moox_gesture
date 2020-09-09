# coding:utf-8
from collections import deque
import numpy as np
import math
import os
import configparser

class Act_Hand_Swing:
    def __init__(self, threshold=20, window_size=5):
        # 肘基準で拳が動き続ける状態 1.0s平均で、しきい値以上の運動をしているか？
        # 読み込み用軸パラメータ
        self.axis = axis = 3
        self.window_size = window_size
        # しきい値^
        self.threshold = threshold

        # 設定読み込み
        inifile = configparser.ConfigParser()
        inifile.read(os.path.dirname(os.path.abspath(__file__)) + '/../../../../../../config.ini', 'UTF-8')

        # 計算入力
        self.r_wrist = np.zeros((axis))
        self.l_wrist = np.zeros((axis))
        self.r_elbow = np.zeros((axis))
        self.l_elbow = np.zeros((axis))
        self.r_handtip = np.zeros((axis))
        self.l_handtip = np.zeros((axis))
        self.r_hand = np.zeros((axis))
        self.l_hand = np.zeros((axis))
        self.r_thumb = np.zeros((axis))
        self.l_thumb = np.zeros((axis))
        self.head = np.zeros((axis))
        self.chest = np.zeros((axis))
        self.naval = np.zeros((axis))
        self.nose = np.zeros((axis))

        movement_window = inifile.getint('gesture_recognition','movement_window')
        self.thresh_small = inifile.getint('gesture_recognition','thresh_wave_small')
        self.thresh_med = inifile.getint('gesture_recognition','thresh_wave_medium')
        self.thresh_large = inifile.getint('gesture_recognition','thresh_wave_large')
        self.handtip_L_x_recent = deque([0],maxlen=movement_window)
        self.handtip_R_x_recent = deque([0],maxlen=movement_window)
        self.handtip_L_z_recent = deque([0],maxlen=movement_window)
        self.handtip_R_z_recent = deque([0],maxlen=movement_window)

        self.is_r_hand_swing = 0
        self.is_l_hand_swing = 0
        self.is_hand_swing = 0

        self.window_move_hilo_R = deque([0],maxlen=movement_window)
        self.window_move_hilo_L = deque([0],maxlen=movement_window)
        self.window_move_hilo_R_z = deque([0],maxlen=movement_window)
        self.window_move_hilo_L_z = deque([0],maxlen=movement_window)


    def calculate(self,
                  r_wrist=np.zeros(3),
                  l_wrist=np.zeros(3),
                  r_elbow=np.zeros(3),
                  l_elbow=np.zeros(3),
                  r_handtip=np.zeros(3),
                  l_handtip=np.zeros(3),
                  r_hand=np.zeros(3),
                  l_hand=np.zeros(3),
                  r_thumb=np.zeros(3),
                  l_thumb=np.zeros(3),
                  head=np.zeros(3),
                  chest=np.zeros(3),
                  naval=np.zeros(3),
                  nose=np.zeros(3),
                  is_data=False):
        # 初期値
        self.is_hand_swing = 0
        self.is_r_hand_swing = 0
        self.is_l_hand_swing = 0
        self.is_r_hand_swing_z = 0
        self.is_l_hand_swing_z = 0

        is_r_hand_up = False
        is_l_hand_up = False
        is_hand_up = False

        x_idx = 0
        y_idx = 1
        z_idx = 2

        thresh_small = self.thresh_small
        thresh_med = self.thresh_med
        thresh_large = self.thresh_large
        boundary_line = 10

        l_handtip_dif = 0
        r_handtip_dif = 0
        l_handtip_dif_z = 0
        r_handtip_dif_z = 0


        flag_movebothways_L = False
        flag_movebothways_R = False
        flag_movebothways_L_z = False
        flag_movebothways_R_z = False


        if (is_data):

            l_handtip_dif = l_handtip[x_idx] -self.handtip_L_x_recent[-1]
            r_handtip_dif = r_handtip[x_idx] -self.handtip_R_x_recent[-1]
            if abs(l_handtip_dif) < 600:
                self.handtip_L_x_recent.append(l_handtip[x_idx])
                if l_handtip_dif > 0:
                    self.window_move_hilo_L.append(1)
                else:
                    self.window_move_hilo_L.append(-1)
            if abs(r_handtip_dif) < 600: #-# Same as left hand
                self.handtip_R_x_recent.append(r_handtip[x_idx])
                if r_handtip_dif > 0:
                    self.window_move_hilo_R.append(1)
                else:
                    self.window_move_hilo_R.append(-1)

            if abs(np.sum(self.window_move_hilo_L)) < 3:
                flag_movebothways_L = True
            if abs(np.sum(self.window_move_hilo_R)) < 3:
                flag_movebothways_R = True


            l_handtip_dif_z = l_handtip[z_idx] -self.handtip_L_z_recent[-1]
            r_handtip_dif_z = r_handtip[z_idx] -self.handtip_R_z_recent[-1]
            if abs(l_handtip_dif_z) < 600:
                self.handtip_L_z_recent.append(l_handtip[z_idx])
                if l_handtip_dif_z > 0:
                    self.window_move_hilo_L_z.append(1)
                else:
                    self.window_move_hilo_L_z.append(-1)
            if abs(r_handtip_dif) < 600:
                self.handtip_R_z_recent.append(r_handtip[z_idx])
                if r_handtip_dif > 0:
                    self.window_move_hilo_R_z.append(1)
                else:
                    self.window_move_hilo_R_z.append(-1)

            if abs(np.sum(self.window_move_hilo_L_z)) < 3:
                flag_movebothways_L_z = True
            if abs(np.sum(self.window_move_hilo_R_z)) < 3:
                flag_movebothways_R_z = True

            self.is_hand_swing = 0
            self.is_l_hand_swing = 0
            self.is_r_hand_swing = 0

            move_amnt_R = np.percentile(self.handtip_R_x_recent,90) - np.percentile(self.handtip_R_x_recent,10)
            move_amnt_L = np.percentile(self.handtip_L_x_recent,90) - np.percentile(self.handtip_L_x_recent,10)

            if flag_movebothways_R:
                if (move_amnt_R) > thresh_small:
                    if r_wrist[y_idx] > r_elbow[y_idx]:
                        if (r_wrist[y_idx] > naval[y_idx]):
                            is_r_hand_up = True
                            self.is_r_hand_swing = 1
                            if (move_amnt_R) > thresh_large:
                                self.is_r_hand_swing = 3
                            elif (move_amnt_R) > thresh_med:
                                self.is_r_hand_swing = 2
            if flag_movebothways_L: #NCP
                if (move_amnt_L) > thresh_small:
                    if l_wrist[y_idx] > l_elbow[y_idx]:
                        if (l_wrist[y_idx] > naval[y_idx]):
                            is_l_hand_up = True
                            self.is_l_hand_swing = 1
                            if (move_amnt_L) > thresh_large:
                                self.is_l_hand_swing = 3
                            elif (move_amnt_L) > thresh_med:
                                self.is_l_hand_swing = 2

## Z Block 2 - Start
            move_amnt_R_z = np.percentile(self.handtip_R_z_recent,90) - np.percentile(self.handtip_R_z_recent,10)
            move_amnt_L_z = np.percentile(self.handtip_L_z_recent,90) - np.percentile(self.handtip_L_z_recent,10)

            if flag_movebothways_R_z:
                if (move_amnt_R) > thresh_small:
                    if r_wrist[y_idx] > r_elbow[y_idx]:
                        if (r_wrist[y_idx] > naval[y_idx]):
                            is_r_hand_up = True
                            self.is_r_hand_swing_z = 1
                            if (move_amnt_R) > thresh_large:
                                self.is_r_hand_swing_z = 3
                            elif (move_amnt_R) > thresh_med:
                                self.is_r_hand_swing_z = 2
            if flag_movebothways_L_z:
                if (move_amnt_L_z) > thresh_small:
                    if l_wrist[y_idx] > l_elbow[y_idx]:
                        if (l_wrist[y_idx] > naval[y_idx]):
                            is_l_hand_up = True
                            self.is_l_hand_swing_z = 1
                            if (move_amnt_L_z) > thresh_large:
                                self.is_l_hand_swing_z = 3
                            elif (move_amnt_L_z) > thresh_med:
                                self.is_l_hand_swing_z = 2

## Z Block 2 - End

            swing_val = []
            swing_val.append(self.is_r_hand_swing)
            swing_val.append(self.is_l_hand_swing)
            swing_val.append(self.is_r_hand_swing_z)
            swing_val.append(self.is_l_hand_swing_z)
            self.is_hand_swing = max(swing_val)

        return self.is_hand_swing, self.is_r_hand_swing, self.is_l_hand_swing
