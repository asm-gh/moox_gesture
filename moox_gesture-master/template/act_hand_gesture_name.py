# coding:utf-8
from collections import deque
import numpy as np
import math
import os
import configparser

class Act_Hand_Gesture_Name:
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
        self.handtip_L_x_recent = deque(maxlen=movement_window) #NCP Edit
        self.handtip_R_x_recent = deque(maxlen=movement_window) #NCP Edit

        self.is_r_hand_push = 0
        self.is_l_hand_push = 0
        self.is_hand_push = 0

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
        self.is_hand_gesture_name = 0
        self.is_l_hand_gesture_name = 4
        self.is_r_hand_gesture_name = 4

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

            self.is_hand_gesture_name = 0
            self.is_l_hand_gesture_name = 0
            self.is_r_hand_gesture_name = 0

            move_amnt_R = np.percentile(self.handtip_R_x_recent,90) - np.percentile(self.handtip_R_x_recent,10)
            move_amnt_L = np.percentile(self.handtip_L_x_recent,90) - np.percentile(self.handtip_L_x_recent,10)


            push_threshold = .8
            r_elbow_wrist_z = (r_elbow[z_idx] - r_wrist[z_idx])
            r_elbow_wrist_d = push_threshold*(np.linalg.norm(r_elbow - r_wrist))
            l_elbow_wrist_z = (l_elbow[z_idx] - lwrist[z_idx])
            l_elbow_wrist_d = push_threshold*(np.linalg.norm(l_elbow - l_wrist))

            #Conditional Statement Below-------


            #Conditional Statement Above-------
                
            push_val = []
            push_val.append(self.is_r_hand_gesture_name)
            push_val.append(self.is_l_hand_gesture_name)
            self.is_hand_push = max(push_val)

        return self.is_hand_gesture_name, self.is_r_hand_gesture_name, self.is_l_hand_gesture_name
