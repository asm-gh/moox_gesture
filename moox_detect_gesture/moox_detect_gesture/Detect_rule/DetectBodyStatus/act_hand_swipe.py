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

            self.is_hand_swipe = 0
            self.is_l_hand_swipe = 0
            self.is_r_hand_swipe = 0


            move_amnt_R = np.percentile(self.handtip_R_x_recent,90) - np.percentile(self.handtip_R_x_recent,10)
            move_amnt_L = np.percentile(self.handtip_L_x_recent,90) - np.percentile(self.handtip_L_x_recent,10)


            if (move_amnt_R) > thresh_small:
                if r_wrist[y_idx] > r_elbow[y_idx]:
                    if (r_wrist[x_idx] > boundary_line):
                        if (r_wrist[y_idx] > naval[y_idx]):
                            if (move_amnt_R) > thresh_large:
                                self.is_r_hand_swipe = 1

            if (move_amnt_L) > thresh_small:
                if l_wrist[y_idx] > l_elbow[y_idx]:
                    if (l_wrist[x_idx] > boundary_line):
                        if (l_wrist[y_idx] > naval[y_idx]):
                            if (move_amnt_L) > thresh_large:
                                self.is_l_hand_swipe = 1
                
            swipe_val = []
            swipe_val.append(self.is_r_hand_swipe)
            swipe_val.append(self.is_l_hand_swipe)
            self.is_hand_swipe = max(swipe_val)

        return self.is_hand_swipe, self.is_r_hand_swipe, self.is_l_hand_swipe
