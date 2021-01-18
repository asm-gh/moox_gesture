# coding:utf-8
from collections import deque
import numpy as np
import math
import os
import configparser

class Act_Hand_Up:
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
        self.hand_ht = inifile.getint('gesture_recognition','hand_ht')

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

        self.is_r_hand_up = 0
        self.is_l_hand_up = 0
        self.is_hand_up = 0

        #Throw Seeds Parts
        deque_z_size = 15 #move this to INI when fixed
        deque_cooldown_size = 30
        deque_timecooldown_size = 30
        self.hand_L_z_recent = deque([0],maxlen=deque_z_size)
        self.hand_R_z_recent = deque([0],maxlen=deque_z_size)
        # self.region_cooldown_l = deque([0],maxlen=deque_cooldown_size)
        # self.region_cooldown_r = deque([0],maxlen=deque_cooldown_size)
        self.time_cooldown_l = deque([0],maxlen=deque_timecooldown_size)
        self.time_cooldown_r = deque([0],maxlen=deque_timecooldown_size)

        self.is_r_throwseed = 0
        self.is_l_throwseed = 0
        self.is_throwseed = 0

        #Can put the INI grabs here

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
        self.is_r_throwseed = 0
        self.is_l_throwseed = 0
        self.is_throwseed = 0

        x_idx = 0
        y_idx = 1
        z_idx = 2

        if (is_data):
            #Idea possibles - could just do the region with region lock cool down, motion back requires the velocity anyway
            # Time based cooldown might be better in Unity?
            ### Velocity Check ###
            #store z locations
            self.hand_L_z_recent.append(l_hand[z_idx])
            self.hand_R_z_recent.append(r_hand[z_idx])
            #check for z motion last point minus first to check for positive z motion (make sure this works, some rare cases might break this (like very fast motion))
                #but the alternative is much longer code I think
            check_z_motion_L = (self.hand_L_z_recent[-1]) - (self.hand_L_z_recent[0])
            check_z_motion_R = (self.hand_R_z_recent[-1]) - (self.hand_R_z_recent[0])

            ### Checks ###
            # 1. Is hand above naval y
            # 2. Is hand z beyond naval z + some
            # 3. Is hand_z motion greater than some amount
            # 4. Is the timer cooldown expired

            #LEFT
            if l_hand[y_idx] > naval[y_idx]:
                if l_hand[z_idx] > naval[z_idx] + 200: #Calibrate this and maybe use knee instead and move to INI
                    if check_z_motion_L > 100: #calibrate and move to INI
                        if max(self.time_cooldown_l) < 1:
                            self.is_l_throwseed =1
                            self.time_cooldown_l.append(1)
            #RIGHT
            if r_hand[y_idx] > naval[y_idx]:
                if r_hand[z_idx] > naval[z_idx] + 200: #Calibrate this and maybe use knee instead and move to INI
                    if check_z_motion_R > 100: #calibrate and move to INI
                        if max(self.time_cooldown_r) < 1:
                            self.is_r_throwseed =1
                            self.time_cooldown_r.append(1)


            # if throw seed isn't hit, put 0s in the time counter, when all 0, it can go again
            if self.is_r_throwseed == 0:
                self.time_cooldown_r.append(0)
            if self.is_l_throwseed == 0:
                self.time_cooldown_l.append(0)

            #Check to set is_throwseed should be 1
            up_val = []
            up_val.append(self.is_l_throwseed)
            up_val.append(self.is_r_throwseed)
            self.is_throwseed = max(up_val)


            return self.is_throwseed, self.is_r_throwseed, self.is_l_throwseed



##### Older saving just as ideas - Delete in final version ######
    #### Skipped the region lockout in favor of time, because velocity should be okay
        # if r_hand[y_idx] > naval[y_idx]:
        #     if r_hand[z_idx] > naval[z_idx] + 200: #Calibrate this and maybe use knee instead and move to INI
        #     #     self.region_cooldown_l.append(1)
        #     # else:
        #     #     self.region_cooldown_l.append(0)
        #         if check_z_motion_R > 100: #calibrate and move to INI
        #             # if min(self.region_cooldown) == 0:
        #             if max(self.time_cooldown_r) < 1:
        #                 self.is_r_throwseed =1
        #                 self.time_cooldown_r.append(1)
