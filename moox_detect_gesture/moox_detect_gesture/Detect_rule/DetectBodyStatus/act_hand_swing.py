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
        self.handtip_L_x_recent = deque(maxlen=movement_window)
        self.handtip_R_x_recent = deque(maxlen=movement_window)

        self.is_r_hand_swing = 0
        self.is_l_hand_swing = 0
        self.is_hand_swing = 0


        self.window_move_hilo_R = deque(maxlen=movement_window) #NCP
        self.window_move_hilo_L = deque(maxlen=movement_window) #NCP

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
        self.is_hand_swing = False
        self.is_r_hand_swing = 4
        self.is_l_hand_swing = 4
        self.is_l_hand_swipe = 4
        self.is_r_hand_swipe = 4
        self.is_l_hand_push = 4
        self.is_r_hand_push = 4

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

        l_handtip_dif = 0 #NCP
        r_handtip_dif = 0 #NCP

        flag_movebothways_L = False
        flag_movebothways_R = False

        if (is_data):

            #NCP New 9/8 - Start of Block

            #-# Denotes Plain English Version
            l_handtip_dif = l_handtip[x_idx]-handtip_L_x_recent[movement_window-1] #-# New Handtip point - Most Recent Handtip point
            r_handtip_dif = r_handtip[x_idx]-handtip_R_x_recent[movement_window-1]
            if abs(l_handtip_dif) < 600: #-# Checks for outliers. If new value is too far from old, ignore it
                self.handtip_L_x_recent.append(l_handtip[x_idx])
                if l_handtip_dif > 0: #-# If new point is higher, window_move_hilo_L is 1. If less window_move_hilo_L is -1
                    self.window_move_hilo_L.append(1)
                else:
                    self.window_move_hilo_L.append(-1)
            if abs(r_handtip_dif) < 600: #-# Same as left hand
                self.handtip_R_x_recent.append(r_handtip[x_idx])
                if r_handtip_dif > 0:
                    self.window_move_hilo_R.append(1)
                else:
                    self.window_move_hilo_R.append(-1)

            #-# if low (<3 for now), the value l_handtip_dif was varying between + and -
            #-# if higher, that means the value varied mostly in one direction (indicating a swipe, not wave)
            if abs(np.sum(self.window_move_hilo_L)) < 3:
                flag_movebothways_L = True
            if abs(np.sum(self.window_move_hilo_R)) < 3:
                flag_movebothways_R = True

            #NCP New 9/8 - End of Block



            self.is_hand_swing = 0
            self.is_l_hand_swing = 0
            self.is_r_hand_swing = 0

            move_amnt_R = np.percentile(self.handtip_R_x_recent,90) - np.percentile(self.handtip_R_x_recent,10)
            move_amnt_L = np.percentile(self.handtip_L_x_recent,90) - np.percentile(self.handtip_L_x_recent,10)

            if flag_movebothways_R: #NCP
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
                
            swing_val = []
            swing_val.append(self.is_r_hand_swing)
            swing_val.append(self.is_l_hand_swing)
            self.is_hand_swing = max(swing_val)

        return self.is_hand_swing, self.is_r_hand_swing, self.is_l_hand_swing
