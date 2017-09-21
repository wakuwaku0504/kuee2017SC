# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 18:03:19 2017

@author: TE058
"""

import cv2
import cv2.aruco as aruco
import numpy as np

class Coordinates(object):
    def __init__(self, id):
        self.cap1 = cv2.VideoCapture(self.camera1_id)
        self.cap2 = cv2.VideoCapture(self.camera2_id)
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        #playerのid
        self.id = id
        #キャリブレーション定数
        self.K = np.loadtxt('K.csv', delimiter=',')
        self.d = np.loadtxt('d.csv', delimiter=',')
        
    
    #player_idに対応する中心座標を返す
    def _get_xys(self, id, ids, corners):
        for i,player in enumerate(ids):
            if player==id:
                s = corners[i].sum(axis=1)
                return s[0]/4

    
    def get(self):
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()
        if not(ret1) and not(ret2):
            return False
        
        corners1, ids1, _ = aruco.detectMarkers(frame1, self.dictionary)
        corners2, ids2, _ = aruco.detectMarkers(frame2, self.dictionary)
        if ids1 is None:
            if ids2 is None:
                return False
            else:
                xy2 = self._get_xys(self.id, ids2, corners2)
                return xy2
        elif ids2 is None:
            if ids1 is None:
                return False
            else:
                xy1 = self._get_xys(self.id, ids1, corners1)
                return xy1
        else:
            xy1 = self._get_xys(self.id, ids1, corners1)
            xy2 = self._get_xys(self.id, ids2, corners2)
            return xy1
    
    
    def image(self):
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()
        if not(ret1) and not(ret2):
            return False
        
        corners1, ids1, _ = aruco.detectMarkers(frame1, self.dictionary)
        corners2, ids2, _ = aruco.detectMarkers(frame2, self.dictionary)
        if (ids1 is None) and (ids2 is None):
            return False
        
        undistort_image1 = cv2.undistort(frame1, self.K, self.d)
        undistort_image2 = cv2.undistort(frame2, self.K, self.d)
        image1 = aruco.drawDetectedMarkers(undistort_image1, corners1, ids1)
        image2 = aruco.drawDetectedMarkers(undistort_image2, corners2, ids2)
 
        cv2.imshow("camera1", image1)
        cv2.imshow("camera2", image2)
        
    def release(self):
        self.cap1.release()
        self.cap2.release
    
    
if __name__=="__main__":
    Coordinates.camera1_id = 1
    Coordinates.camera2_id = 2
    coor = Coordinates(0)
    
    while(1):
        #coor.image()
        xy = coor.get()
        print(xy)
        # qを押したら終了
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    
    
    coor.release()
    cv2.destroyAllWindows()