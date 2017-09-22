# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 18:03:19 2017

@author: TE058
"""

import cv2
import cv2.aruco as aruco
import numpy as np

class Coordinates(object):
    def __init__(self, player_id, camera_id):
        self.cap = cv2.VideoCapture(camera_id)
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        #playerのid
        self.id = player_id
        #キャリブレーション定数
        self.K = np.loadtxt('calib/K.csv', delimiter=',')
        self.d = np.loadtxt('calib/d.csv', delimiter=',')
        
    
    #player_idに対応する中心座標を返す
    def _get_xys(self, id, ids, corners):
        for i,player in enumerate(ids):
            if player==id:
                s = corners[i].sum(axis=1)
                return s[0]/4

    
    def get(self):
        ret, frame = self.cap.read()
        if not ret:
            return False
        #print(frame.shape)
        corners, ids, _ = aruco.detectMarkers(frame, self.dictionary)
        if ids is None:
            return False
        
        xy = self._get_xys(self.id, ids, corners)
        if xy is None:
            return False
        return xy[0]/640, xy[1]/480
    
    
    
    def image(self):
        ret, frame = self.cap.read()
        if not ret:
            return False
        
        corners, ids, _ = aruco.detectMarkers(frame, self.dictionary)
        if ids is None:
            return False
        
        undistort_image = cv2.undistort(frame, self.K, self.d)
        
        image = aruco.drawDetectedMarkers(undistort_image, corners, ids)
        
 
        cv2.imshow("camera", image)

        
    def release(self):
        self.cap.release()

    
    
if __name__=="__main__":
    coo = Coordinates(player_id=0,camera_id=2)
    
    while(1):
        coo.image()
        #xy = coo.get()
        #if not xy==False:
        #    print(xy[0],xy[1])
        #else:
         #   pass
        # qを押したら終了
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    
    
    coo.release()
    cv2.destroyAllWindows()