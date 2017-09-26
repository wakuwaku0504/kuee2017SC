# -*- coding: utf-8 -*-
"""
Created on Thu Sep  7 09:05:59 2017

@author: TE058
"""

import pygame
from pygame.locals import *
from sprites import SCR_RECT 
import sys
import cv2
import numpy as np
import os
import random

def joystick(flag):
    pygame.joystick.init()
    try:
        stick = pygame.joystick.Joystick(flag-1) # create a joystick instance
        stick.init() # init instance
        print('Joystickの名称: ' + stick.get_name())
        print('ボタン数 : ' + str(stick.get_numbuttons()))
        return stick
    except pygame.error:
        print('Joystickが見つかりませんでした。')
        return False

def resize(image, w, h):
    img = cv2.imread(image, cv2.IMREAD_COLOR)
    re_img = cv2.resize(img, (w,h))
    name, _ = os.path.splitext(image)
    path = name + "_resized.png"
    cv2.imwrite(path, re_img)

#画像をリサイズして読み込む
def load_image(filename, width, height, colorkey=None):
    resize(filename, width, height)
    name, _ = os.path.splitext(filename)
    filename = name + "_resized.png"
    try:
        image = pygame.image.load(filename)
    except (pygame.error, message):
        print("Cannot load image:", filename)
        raise (SystemExit, message)
        
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    os.remove(filename)
    return image

def change_tile_group(tiles0, tiles1, tiles2, tile, newg):
    if newg==1:
        if tile.flag==0:
            tiles0.remove(tile)
        elif tile.flag==2:
            tiles2.remove(tile)
        tiles1.add(tile)
        tile.flag = 1
        tile.change_to_1()
    elif newg==2:
        if tile.flag==0:
            tiles0.remove(tile)
        elif tile.flag==1:
            tiles1.remove(tile)
        tiles2.add(tile)
        tile.flag = 2
        tile.change_to_2()
    
    
#shots1とtiles0かtiles2のスプライトグループの衝突を判定
def collision_detection1(tiles0, tiles1, tiles2, shots1):
    tile_collided_0 = pygame.sprite.groupcollide(tiles0, shots1, False, True)
    tile_collided_2 = pygame.sprite.groupcollide(tiles2, shots1, False, True)
    tile_collided_0.update(tile_collided_2)
    
    for tile in tile_collided_0.keys():
        change_tile_group(tiles0, tiles1, tiles2, tile, 1)

#shots2とtiles0かtiles１の数ライトグループの衝突を判定
def collision_detection2(tiles0, tiles1, tiles2, shots2):
    tile_collided_0 = pygame.sprite.groupcollide(tiles0, shots2, False, True)
    tile_collided_1 = pygame.sprite.groupcollide(tiles1, shots2, False, True)
    tile_collided_0.update(tile_collided_1)
    
    for tile in tile_collided_0.keys():
        change_tile_group(tiles0, tiles1, tiles2, tile, 2)


#スコアを計上する
def calc_score(tiles0, tiles1, tiles2):
    score0 = len(list(tiles0))
    score1 = len(list(tiles1))
    score2 = len(list(tiles2))
    return score0, score1, score2
    
#ランダムにタイルを選んで座標取得
def gene_item(tiles0, tiles1, tiles2):
    tiles = tuple(tiles0) + tuple(tiles1) + tuple(tiles2)
    tile = random.choice(tiles)
    return tile.rect.centerx, tile.rect.centery

#高さの判定
#def judge_height(height):
#    if 1500<height<2800:
#        return True
#    else:
#        return False
    
#フィールド内判定
#def judge_field(pos):
#    if 0<pos[0]<SCR_RECT.width and 0<pos[1]<SCR_RECT.height:
#        return True
#    else:
#        return False
    
    
        