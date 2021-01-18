# coding:utf-8
from collections import deque
import numpy as np
import math
import os
import configparser

class Act_Hand_Clap:
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
        self.hand_distance = inifile.getint('gesture_recognition','hand_distance')

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

        self.is_r_hand_clap = 0
        self.is_l_hand_clap = 0
        self.is_hand_clap = 0

        #Shuriken part
        deque_size_handdistances = 15
        self.handclap_history = deque([0,0],maxlen=2)
        self.hand_l_x_hist = deque([0],deque_size_handdistances)
        self.hand_l_y_hist = deque([0],deque_size_handdistances)
        self.hand_l_z_hist = deque([0],deque_size_handdistances)
        self.hand_r_x_hist = deque([0],deque_size_handdistances)
        self.hand_r_y_hist = deque([0],deque_size_handdistances)
        self.hand_r_z_hist = deque([0],deque_size_handdistances)

        self.hand_l_hist = deque([0],deque_size_handdistances)
        self.hand_r_hist = deque([0],deque_size_handdistances)

        self.shuriken_origin = np.zeros(3)

        self.shuriken_counter = 0

        self.throw_shuriken = 0
        self.shuriken_direction = np.zeros(3)


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
        self.is_r_hand_clap = 0
        self.is_l_hand_clap = 0
        self.is_hand_clap = 0
        hand_distance = self.hand_distance

        x_idx = 0
        y_idx = 1
        z_idx = 2


        if (is_data):
            self.is_hand_clap = 0
            if l_hand[y_idx] > naval[y_idx] or r_hand[y_idx] > naval[y_idx] :
                hand_dist = np.linalg.norm(l_hand - r_hand)
                if hand_dist < hand_distance:
                    self.is_hand_clap = 1


            # Shuriken specific part

            #Store the locations
            # self.hand_l_x_hist.append(l_hand[x_idx])
            # self.hand_l_y_hist.append(l_hand[y_idx])
            # self.hand_l_z_hist.append(l_hand[z_idx])
            # self.hand_r_x_hist.append(r_hand[x_idx])
            # self.hand_r_y_hist.append(r_hand[y_idx])
            # self.hand_r_z_hist.append(r_hand[z_idx])
            self.hand_l_hist.append(l_hand)
            self.hand_r_hist.append(r_hand)

            #store last 2 claps to know if it changes
            self.handclap_history.append(self.is_hand_clap)


            if self.handclap_history[0] - self.handclap_history[-1] == 1: #if switch from clap to not clap
                if shuriken_counter == 0:
                    self.shuriken_counter = 15 #set shuriken counter

            if self.shuriken_counter > 0:
                self.shuriken_counter -= 1
                if self.shuriken_counter == 0: #if the counter hits 0
                    self.throw_shuriken = 1 #throw shuriken flag to True
                    #Get throw distances/directions
                    throw_dist_L = np.linalg.norm(self.hand_l_hist[-1] - self.hand_l_hist[0])
                    throw_dist_R = np.linalg.norm(self.hand_r_hist[-1] - self.hand_r_hist[0])

                    # set the direction vector to the hand that moves most and publish it
                    if throw_dist_L > throw_dist_R:
                        self.shuriken_direction = self.hand_l_hist[-1] - self.hand_l_hist[0]
                    else:
                        self.shuriken_direction = self.hand_r_hist[-1] - self.hand_r_hist[0]




        return self.throw_shuriken, self.shuriken_direction


#Overview
    # When clap goes from 1 -> 0
    # Start a counter (15)
    # When counter hits 0, check the hand distances from current frame to when counter started
    # Pass throw shuriken flag and direction (from greater hand movement between L and R)






#Alternative would be lose the clap and just look for velocites like in throw seeds and could pass direction too
