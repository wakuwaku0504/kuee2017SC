# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 07:57:56 2017

@author: TE058
"""

class Config(object):
    def __init__(self, self_image, sp_image, tile, support):
        self.image = "image/{}".format(self_image)
        self.sp_image = "image/{}".format(sp_image)
        self.tile = "image/{}".format(tile)
        self.support = "image/{}".format(support)                

#チーム設定
jobs = Config("jobs.jpg","jobs2.jpg","mac.png","apple.png")

gates = Config("gates.jpg","gates2.jpg","windows.jpg","microsoft.jpg")

saki = Config("saki.jpg", "saki2.jpg", "hai.jpg", "nodoka.jpg")

nodoka = Config("nodo.jpg", "nodo2.jpg", "isou.jpg", "etopen.jpg")

aphex = Config("Aphex.jpg", "Aphex2.jpg", "aphex_tile.png", "aphex_sup.jpg")
A = Config("A/plane.JPG","A/plane.JPG","A/tile.jpg","A/support.png")
B = Config("B/plane.jpg","B/plane.jpg","B/tile.jpg","B/support.jpg")
C = Config("C/plane.png","C/plane.png","C/tile.png","C/support.png")
D = Config("D/plane.jpg","D/plane.jpg","D/tile.jpg","D/support2.png")
shibuya_kun = Config("keigo.jpg", "keigo2.jpg", "head.jpg", "point.jpg")
