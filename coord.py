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
        if not self.cap.isOpened():
            raise OSError("camera wasn't opened")
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        #playerのid
        self.id = player_id
        #キャリブレーション定数
        if camera_id == 0:
            self.K = np.loadtxt('calib/K_170925.csv', delimiter=',')
            self.d = np.loadtxt('calib/d_170925.csv', delimiter=',')
        elif camera_id == 2:
            self.K = np.loadtxt('calib/K_170925_2.csv', delimiter=',')
            self.d = np.loadtxt('calib/d_170925_2.csv', delimiter=',')            
            
        #カメラの解像度
        self.width = 640
        self.height = 480
        #この倍率でクロップする
        self.crop_h = 0.9
        self.crop_w = 1
        #新しい解像度
        self.width_c = int(self.width*self.crop_w)
        self.height_c = int(self.height*self.crop_h)
        self.w_bias = int((self.width - self.width_c)/2)
        self.h_bias = int((self.height - self.height_c)/2)
        #imageの切り取るインデックス
        self.w_start = self.w_bias
        self.w_end = self.w_bias + self.width_c
        self.h_start = self.h_bias
        self.h_end = self.h_bias + self.height_c
    
    #imageの中央のある割合を切り取って返す
    def crop_image(self, image):
        return image[self.h_start:self.h_end, self.w_start:self.w_end]
        
    
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
        
        undistort_image = cv2.undistort(frame, self.K, self.d)
    
        #print(undistort_image.shape)
        corners, ids, _ = aruco.detectMarkers(undistort_image, self.dictionary)
        if ids is None:
            return False
        
        xy = self._get_xys(self.id, ids, corners)
        if xy is None:
            return False
        return (xy[0]-self.w_bias)/self.width_c, (xy[1]-self.h_bias)/self.height_c
    
    
    
    def image(self,dis):
        ret, frame = self.cap.read()
        #print(ret)
        if not ret:
            return False
        
        undistort_image = cv2.undistort(frame, self.K, self.d)
        #print(cropped_image.shape)
        corners, ids, _ = aruco.detectMarkers(undistort_image, self.dictionary)
        if ids is None:
            return False
        
        #cropped_image = self.crop_image(undistort_image)
        image = aruco.drawDetectedMarkers(undistort_image, corners, ids)
        
        cv2.imshow("camera{}".format(dis), image)

        
    def release(self):
        self.cap.release()

    
    
if __name__=="__main__":
    coo1 = Coordinates(player_id=1,camera_id=0)
    #coo2 = Coordinates(player_id=3,camera_id=2)
    
    while(1):
        coo1.image(0)
        #coo2.image(2)
        #xy = coo.get()
        #if not xy==False:
        #    print(xy[0],xy[1])
        #else:
        #    pass
        # qを押したら終了
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
    
    
    coo1.release()
    #coo2.release()
    cv2.destroyAllWindows()