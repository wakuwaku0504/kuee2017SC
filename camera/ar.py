# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 14:29:00 2017

@author: TE058
"""
import cv2
import cv2.aruco as aruco

id = 4

dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
marker = aruco.drawMarker(dictionary, id, 600)

if __name__=='__main__':
    
    img = cv2.imread('ar_sample.png')
    #img = cv2.resize(img, None, fx=0.05, fy=0.05)
    
    #cv2.imshow("image", img)
    cv2.imshow("marker", marker)
    
    #corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)
    cv2.waitKey(0)
    cv2.destroyAllWindows()    
    
    cv2.imwrite("marker_{}.png".format(id), marker)
    #print(corners)
    #print(ids)
    #print(rejectedImgPoints)