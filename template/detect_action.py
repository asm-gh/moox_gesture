#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np

# 行動推定用ルール
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from act_hand_gesture_name import Act_Hand_Gesture_Name

class Detect_action:
    def __init__(self, axis=3):
        # set parameter
        self.axis = axis
        self.axis_tank = ['x', 'y', 'z']
        self.is_data = False
        # set data
        self.pelvis = np.zeros((axis))
        self.naval = np.zeros((axis))
        self.chest = np.zeros((axis))
        self.neck = np.zeros((axis))
        self.l_clavicle = np.zeros((axis))
        self.r_clavicle = np.zeros((axis))
        self.l_shoulder = np.zeros((axis))
        self.r_shoulder = np.zeros((axis))
        self.l_elbow = np.zeros((axis))
        self.r_elbow = np.zeros((axis))
        self.l_wrist = np.zeros((axis))
        self.r_wrist = np.zeros((axis))
        self.l_hip = np.zeros((axis))
        self.r_hip = np.zeros((axis))
        self.l_knee = np.zeros((axis))
        self.r_knee = np.zeros((axis))
        self.l_ankle = np.zeros((axis))
        self.r_ankle = np.zeros((axis))
        self.l_foot = np.zeros((axis))
        self.r_foot = np.zeros((axis))
        self.head = np.zeros((axis))
        self.nose = np.zeros((axis))
        self.l_eyes = np.zeros((axis))
        self.r_eyes = np.zeros((axis))
        self.l_ear = np.zeros((axis))
        self.r_ear = np.zeros((axis))
        self.l_hand = np.zeros((axis))
        self.r_hand = np.zeros((axis))
        self.l_handtip = np.zeros((axis))
        self.r_handtip = np.zeros((axis))
        self.l_thumb = np.zeros((axis))
        self.r_thumb = np.zeros((axis))
        # インスタンス生成

        self.act_hand_gesture_name = Act_Hand_Gesture_Name()
        self.output_data={}

    def Update(self, body_dict):
        axt = self.axis_tank
        for ax in range(self.axis):
            self.l_elbow[ax] = body_dict['l_elbow'][axt[ax]]
            self.l_wrist[ax] = body_dict['l_wrist'][axt[ax]]
            self.r_elbow[ax] = body_dict['r_elbow'][axt[ax]]
            self.r_wrist[ax] = body_dict['r_wrist'][axt[ax]]
            self.r_hand[ax] = body_dict['r_hand'][axt[ax]]
            self.r_handtip[ax] = body_dict['r_handtip'][axt[ax]]
            self.l_hand[ax] = body_dict['l_hand'][axt[ax]]
            self.l_handtip[ax] = body_dict['l_handtip'][axt[ax]]
            self.head[ax] = body_dict['head'][axt[ax]]
            self.chest[ax] = body_dict['chest'][axt[ax]]

    def set_data(self,):
        # 出力データ準備
        dic_data = {}
        # 手を振る
        dic_data['is_hand_swing'] = int(self.is_hand_swing)
        dic_data['is_r_hand_swing'] = int(self.is_r_hand_swing)
        dic_data['is_l_hand_swing'] = int(self.is_l_hand_swing)
        dic_data['is_hand_swipe'] = int(self.is_hand_swipe)
        dic_data['is_r_hand_swipe'] = int(self.is_r_hand_swipe)
        dic_data['is_l_hand_swipe'] = int(self.is_l_hand_swipe)
        dic_data['is_hand_push'] = int(self.is_hand_push)
        dic_data['is_r_hand_push'] = int(self.is_r_hand_push)
        dic_data['is_l_hand_push'] = int(self.is_l_hand_push)
        self.output_data = dic_data

    def Calculate(self, body_dict, is_data=False):
        # データ無しならFalse
        self.is_data = is_data
        if(self.is_data):
            # 骨格データの展開
            self.Update(body_dict)
            # 計算
            # 手を振る
            self.is_hand_gesture_name, self.is_r_hand_gesture_name, self.is_l_hand_gesture_name = \
                self.act_hand_gesture_name.calculate(
                    r_wrist=self.r_wrist,
                    l_wrist=self.l_wrist,
                    r_elbow=self.r_elbow,
                    l_elbow=self.l_elbow,
                    r_handtip=self.r_handtip,
                    l_handtip=self.l_handtip,
                    head=self.head,
                    naval=self.naval,
                    is_data=self.is_data)
        else:
            self.is_hand_swing = 0
            self.is_r_hand_swing = 0
            self.is_l_hand_swing = 0
            self.is_hand_swipe = 0
            self.is_r_hand_swipe = 0
            self.is_l_hand_swipe = 0
            self.is_hand_push = 0
            self.is_r_hand_push = 0
            self.is_l_hand_push = 0
        # データ格納
        self.set_data()
