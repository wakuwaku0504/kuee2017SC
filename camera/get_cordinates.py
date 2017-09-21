# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 16:14:03 2017

@author: TE055
"""
import cv2
import cv2.aruco as aruco
import numpy as np

class Cordinates(object):
    def __init__(self, id):
        self.cap1 = cv2.VideoCapture(self.camera1_id)
        self.cap2 = cv2.VideoCapture(self.camera2_id)
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        #playerのid
        self.id = id
        #カメラ間距離
        self.d  = 100
    #カメラから座標が取れないときに線形に近似する
    #def _extension(self):
        
    #player_idに対応する中心座標を返す
    def _get_xys(self, id, ids, corners):
        for i,player in enumerate(ids):
            if player==id:
                s = corners[i].sum(axis=1)
                return s[0]/4

            
    #直交座標から極座標へ
    def _to_polar(self, x,y):
        radii = np.sqrt(x**2+y**2)
        theta = np.arctan2(y,x)
        return radii, theta
    
    #現在のそれぞれの座標を取り出す   
    def get(self):
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()
        if not (ret1 and ret2):
            return False
        
        corners1, ids1, _ = aruco.detectMarkers(frame1, self.dictionary)
        corners2, ids2, _ = aruco.detectMarkers(frame2, self.dictionary)
        if (ids1 is None) or (ids2 is None):
            return False
        #自分の直交座標（左上が原点）
        xy1 = self._get_xys(self.id, ids1, corners1)
        xy2 = self._get_xys(self.id, ids2, corners2)
        if (xy1 is None) or (xy2 is None):
            return False
            
        #中心座標を計算
        height, width = frame1.shape[:2]
        centerx = width/2
        centery = height/2
        #それぞれのカメラ視点の極座標
        radii1, theta1 = self._to_polar(xy1[0]-centerx,xy1[1]-centery)
        radii2, theta2 = self._to_polar(xy2[0]-centerx,xy2[1]-centery)
        
        if np.tan(theta1)==np.tan(theta2):
            x = self.d*np.tan(theta2)/(np.tan(theta2)-np.tan(theta1))
            y = x*np.tan(theta1)
        else:
            return False
        
        return x, y

if __name__=="__main__":
    Cordinates.camera1_id = 1
    Cordinates.camera2_id = 2
    c = Cordinates(1)
    while(1):
        cors = c.get()
        if cors:
            print(cors)
            
            
            