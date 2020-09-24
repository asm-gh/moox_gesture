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
        deque_size = inifile.getint('gesture_recognition','deque_size')
        self.thresh_small = inifile.getint('gesture_recognition','thresh_wave_small')
        self.thresh_med = inifile.getint('gesture_recognition','thresh_wave_medium')
        self.thresh_large = inifile.getint('gesture_recognition','thresh_wave_large')
        self.boundary_line = inifile.getint('gesture_recognition','boundary_line')
        self.handtip_dif_thresh = inifile.getint('gesture_recognition','handtip_dif_thresh')
        self.hand_offset = inifile.getint('gesture_recognition','hand_offset')
        self.outlier_thresh = inifile.getint('gesture_recognition','outlier_thresh')
        self.outlier_thresh = inifile.getint('gesture_recognition','outlier_thresh')
        self.elbow_offset = inifile.getint('gesture_recognition','elbow_offset')
        self.hand_correction_tip = inifile.getint('gesture_recognition','hand_correction_tip')
        self.boundary_swipe_adj = inifile.getint('gesture_recognition','boundary_swipe_adj')

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

        self.handtip_L_x_recent = deque([0],maxlen=deque_size)
        self.handtip_R_x_recent = deque([0],maxlen=deque_size)
        self.handtip_recent = deque([0],maxlen=deque_size)
        self.window_move_R = deque([0],maxlen=deque_size)
        self.window_move_L = deque([0],maxlen=deque_size)

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
                  r_shoulder=np.zeros(3),
                  l_shoulder=np.zeros(3),
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
        boundary_line = self.boundary_line + 25

        if (is_data):
            if r_wrist[y_idx] < chest[y_idx]:
                self.handtip_R_x_recent = deque([0],maxlen=10)
            if l_wrist[y_idx] < chest[y_idx]:
                self.handtip_L_x_recent = deque([0],maxlen=10)
            if self.is_base_axis(r_shoulder,r_elbow,r_handtip,naval,r_elbow,r_wrist) or self.is_base_axis(r_shoulder,r_elbow,r_handtip,naval,l_elbow,l_wrist):
                move_bothways_L = True
                move_bothways_R = True
                self.is_hand_swipe = 0
                self.is_l_hand_swipe = 0
                self.is_r_hand_swipe = 0

                r_handtip_dif = r_handtip[x_idx] - self.handtip_R_x_recent[-1]
                if r_handtip_dif < self.outlier_thresh:
                    self.handtip_R_x_recent.append(r_handtip[x_idx])
                if r_handtip_dif > self.handtip_dif_thresh:
                    self.window_move_R.append(1)
                elif r_handtip_dif < -self.handtip_dif_thresh:
                    self.window_move_R.append(-1)
                else:
                    self.window_move_R.append(0)
                if max(self.window_move_R)- min(self.window_move_R) == 1:
                    move_bothways_R = False

                if r_wrist[y_idx] > (r_elbow[y_idx] - self.elbow_offset):
                    if (r_wrist[z_idx] > boundary_line):
                        if (r_wrist[y_idx] > naval[y_idx]):
                            if move_bothways_R == False:
                                if r_handtip[y_idx] < (r_hand[y_idx] + self.hand_offset + self.hand_correction_tip):
                                    self.is_r_hand_swipe = 2

                l_handtip_dif = l_handtip[x_idx] - self.handtip_L_x_recent[-1]
                if l_handtip_dif < (self.outlier_thresh):
                    self.handtip_L_x_recent.append(l_handtip[x_idx])
                if l_handtip_dif > self.handtip_dif_thresh:
                    self.window_move_L.append(1)
                elif l_handtip_dif < -self.handtip_dif_thresh:
                    self.window_move_L.append(-1)
                else:
                    self.window_move_L.append(0)
                if max(self.window_move_L)- min(self.window_move_L) == 1:
                    move_bothways_L = False

                if l_wrist[y_idx] > (l_elbow[y_idx] - self.elbow_offset):
                    if (l_wrist[z_idx] > boundary_line):
                        if (l_wrist[y_idx] > naval[y_idx]):
                            if move_bothways_L == False:
                                if l_handtip[y_idx] < (l_hand[y_idx] + self.hand_offset + self.hand_correction_tip):
                                    self.is_l_hand_swipe = 1

            swipe_val = []
            swipe_val.append(self.is_r_hand_swipe)
            swipe_val.append(self.is_l_hand_swipe)
            self.is_hand_swipe = max(swipe_val)

        return self.is_hand_swipe, self.is_r_hand_swipe, self.is_l_hand_swipe

    def is_base_axis(self, shoulder, elbow, handtip, naval, rl_elbow, rl_wrist):
        x_idx = 0
        y_idx = 1
        z_idx = 2

        base_check = 0

        if rl_wrist[y_idx] > naval[y_idx]:
            base_check = 1
            return base_check
        return base_check
