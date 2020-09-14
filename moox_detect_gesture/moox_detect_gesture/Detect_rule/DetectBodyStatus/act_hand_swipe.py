# coding:utf-8
from collections import deque
import numpy as np
import math
import os
import configparser

class Act_Hand_Swipe:
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
        self.handtip_L_x_recent = deque(maxlen=movement_window)
        self.handtip_R_x_recent = deque(maxlen=movement_window)
        self.handtip_L_z_recent = deque(maxlen=movement_window)
        self.handtip_R_z_recent = deque(maxlen=movement_window)
        self.handtip_recent = deque(maxlen=movement_window)
        self.window_move = deque([0],maxlen=movement_window)

        self.is_r_hand_swipe = 0
        self.is_l_hand_swipe = 0
        self.is_hand_swipe = 0

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
        self.is_hand_swipe = 0
        self.is_l_hand_swipe = 0
        self.is_r_hand_swipe = 0


        x_idx = 0
        y_idx = 1
        z_idx = 2

        thresh_small = self.thresh_small
        thresh_med = self.thresh_med
        thresh_large = self.thresh_large
        boundary_line = 10

        if (is_data):
            self.handtip_L_x_recent.append(l_handtip[x_idx])
            self.handtip_R_x_recent.append(r_handtip[x_idx])
            self.handtip_L_z_recent.append(l_handtip[z_idx])
            self.handtip_R_z_recent.append(r_handtip[z_idx])

            self.is_hand_swipe = 0
            self.is_l_hand_swipe = 0
            self.is_r_hand_swipe = 0

            if r_wrist[y_idx] > r_elbow[y_idx]:
                if (r_wrist[x_idx] > boundary_line):
                    if (r_wrist[y_idx] > naval[y_idx]):
                        move_amnt_R = np.percentile(self.handtip_R_x_recent,90) - np.percentile(self.handtip_R_x_recent,10)
                        move_amnt_R_z = np.percentile(self.handtip_R_z_recent,90) - np.percentile(self.handtip_R_z_recent,10)
                        r_handtip_dif = r_handtip[x_idx] - self.handtip_R_x_recent[-1]
                        r_handtip_dif_z = r_handtip[z_idx] - self.handtip_R_z_recent[-1]
                        handtip_dif = r_handtip_dif if r_handtip_dif > r_handtip_dif_z else r_handtip_dif_z
                        r_hand_tip_x = r_handtip[x_idx] if r_handtip_dif > r_handtip_dif_z else r_handtip[z_idx]
                        thresh_amnt_R = move_amnt_R if move_amnt_R > move_amnt_R_z else move_amnt_R_z
                        self.is_r_hand_swipe = 1 if self.get_data(handtip_dif, r_hand_tip_x, thresh_amnt_R) else 0

            if l_wrist[y_idx] > l_elbow[y_idx]:
                if (l_wrist[x_idx] > boundary_line):
                    if (l_wrist[y_idx] > naval[y_idx]):
                        move_amnt_L = np.percentile(self.handtip_L_x_recent,90) - np.percentile(self.handtip_L_x_recent,10)
                        move_amnt_L_z = np.percentile(self.handtip_L_z_recent,90) - np.percentile(self.handtip_L_z_recent,10)
                        l_handtip_dif = l_handtip[x_idx] - self.handtip_L_x_recent[-1]
                        l_handtip_dif_z = l_handtip[z_idx] - self.handtip_L_z_recent[-1]
                        handtip_dif =  l_handtip_dif if l_handtip_dif > l_handtip_dif_z else l_handtip_dif_z
                        l_hand_tip_x = l_handtip[x_idx] if l_handtip_dif > l_handtip_dif_z else l_handtip[z_idx]
                        thresh_amnt_L = move_amnt_L if move_amnt_L > move_amnt_L_z else move_amnt_L_z
                        self.is_l_hand_swipe = 1 if self.get_data(handtip_dif, l_hand_tip_x , thresh_amnt_L) else 0
                
            swipe_val = []
            swipe_val.append(self.is_r_hand_swipe)
            swipe_val.append(self.is_l_hand_swipe)
            self.is_hand_swipe = max(swipe_val)

        return self.is_hand_swipe, self.is_r_hand_swipe, self.is_l_hand_swipe

    def get_data(self, handtip_dif, handtip, move_amnt):
        thresh_small = self.thresh_small
        flag_movebothways = False
        if abs(handtip_dif) < 600:
            self.handtip_recent.append(handtip)
            if handtip_dif > 0:
                self.window_move.append(1)
            else:
                self.window_move.append(-1)
        if abs(np.sum(self.window_move)) < 3:
            flag_movebothways = True

        if flag_movebothways == False:
            if (move_amnt) > thresh_small:
                return True
            else:
                return False
