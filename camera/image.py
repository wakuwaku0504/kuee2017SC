# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 15:34:39 2017

@author: TE058
"""
import cv2.aruco as aruco
import numpy as np
import cv2

# 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
# 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
# 0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い

#画像をbgrからhsvに変換
def BGR2HSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv

#bgrをhsv画像にしてから赤色だけ抽出 
def ext_red(image):
    hsv = BGR2HSV(image)
    
    low_color = np.array([0, 75, 75])
    upper_color = np.array([20, 255, 255])
    
    #low_color2 = np.array([160, 75, 75])
    #upper_color2 = np.array([180, 255, 255])
    # 色を抽出するマスク
    img_mask = cv2.inRange(hsv,low_color,upper_color)
    #img_mask2 = cv2.inRange(hsv,low_color2,upper_color2)
    
    #img_mask3 = np.logical_or(np.asarray(img_mask), np.asarray(img_mask2))
    
    #画像とマスク画像の共通領域
    img_color = cv2.bitwise_and(image, image, mask=img_mask)
    
    return img_color 

if __name__=='__main__':
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise IOError
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    
    while(1):
 
         # フレームを取得
        ret, frame = cap.read()
        if not ret:
            continue

        #img_show(marker)

        camera_mat = np.loadtxt('K.csv', delimiter=',')
        dist_coef = np.loadtxt('d.csv', delimiter=',')
        print("K = \n", camera_mat)
        print("d = ", dist_coef.ravel())
        undistort_image = cv2.undistort(frame, camera_mat, dist_coef)

        corners, ids, rejectedImgPoints = aruco.detectMarkers(undistort_image, dictionary)
        print(corners, ids)
        
        image = aruco.drawDetectedMarkers(undistort_image, corners, ids)
 
        cv2.imshow("SHOW DETECTED MARKER", image)
 
        # qを押したら終了
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
 
    cap.release()
    cv2.destroyAllWindows()