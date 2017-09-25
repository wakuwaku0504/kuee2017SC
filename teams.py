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
#jobs = Config("jobs.jpg","jobs2.jpg","mac.png","apple.png")

#gates = Config("gates.jpg","gates2.jpg","windows.jpg","microsoft.jpg")

player1 = Config("plane_1.png", "plane_1.png", "tile_red.png", "red_turtle.png" )
player2 = Config("plane_2.png", "plane_2.png", "tile_green.png", "green_turtle.png")
