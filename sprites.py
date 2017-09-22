# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 23:22:30 2017

@author: TE058
"""
import pygame
from pygame.locals import *
import sys
import random
import math
from tools import *
from coord import Coordinates

SCR_RECT = Rect(0, 0, 1024, 768)#(1280,720),(1920,1080)
#SCR_RECT = Rect(0, 0, 640, 480)
TILE_W = int(SCR_RECT.bottom / 10) 
TILE_H = int(SCR_RECT.bottom / 10)
SPEED = int(1*TILE_W/60) #playerspeed
RELOAD = 17
SUPP_LIFE = 8 #second サポートキャラの寿命
SUPP_SPEED = int(3*TILE_W/60)#１秒でタイル
ITEM_TIME = 5 #アイテムの復活時間
SHOT_LIFE = 1 #second
SHOT_SPEED = int(2*TILE_W/60) #１秒でタイル三枚分で、１秒で死ぬ
LIMITE = 2 #minute 制限時間 整数
SP_POINT = 100 #ゲージがたまるタイル塗り数

#スプライトではないが
class Card(object):
    def __init__(self, thumb1, thumb2, screen, teams):
        self.thumb1 = thumb1
        self.thumb2 = thumb2
        self.thumb1.active = 1
        #self.thumb2.theta = 90
        for thumb in [self.thumb1,self.thumb2]:
            thumb.screen = screen
            thumb.teams = teams
            thumb.last = len(teams) - 1
            thumb.image = teams[0]
            thumb.rect = thumb.image.get_rect()
        self.thumb1.rect.center = (int(SCR_RECT.width*1/3),SCR_RECT.centery)
        self.thumb2.rect.center = (int(SCR_RECT.width*2/3),SCR_RECT.centery)
        #0になるまで反応しない
        self.hold = 0
        
    def update(self):
        pk = pygame.key.get_pressed()
        if (pk[K_LEFT] or pk[K_RIGHT]) and self.hold==0:
            self.thumb1.active *= -1
            self.thumb2.active *= -1
            self.hold = 10
        self.thumb1.update()
        self.thumb2.update()
        self.hold -= 1
        if self.hold<0:
            self.hold = 0
        
    def draw(self):
        self.thumb2.draw()
        self.thumb1.draw()
        
    def players(self, teams_list):
        p1 = self.thumb1.head
        p2 = self.thumb2.head
        return teams_list[p1], teams_list[p2]


class Thumbnail(pygame.sprite.Sprite):
    #対戦者を選ぶための画像保持
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #リストのどこを見ているかのインデックス
        self.head = 0
        #操作されてるかどうか
        self.active = -1  #-1or1
        #ボタン押されても、0になるまで反応しない
        self.hold = 0 #frame
        #速度
        self.vy = 0
        #最大速度
        self.vy_max = int(TILE_H/15)
        #周波数
        self.freq = 4
        #角度
        self.theta = 0
        
            
        
    
    def next_team(self):
        #active時
        if self.active==1:
            pk = pygame.key.get_pressed()
            if self.hold==0:
                if pk[K_UP]:
                        self.head += 1
                elif pk[K_DOWN]:
                        self.head -= 1
                #インデックスはみ出してないか
                if self.head>self.last:
                        self.head = 0
                elif self.head<0:
                        self.head = self.last
                self.hold = 3
       
        
    def update(self):
        self.theta += self.freq
        self.vy = int(math.cos(math.radians(self.theta))*self.vy_max)
        self.rect.move_ip(0,self.vy)
        if int(self.theta)==360:
            self.theta = 0
        self.next_team()
        self.image = self.teams[self.head]
        
        self.hold -= 1
        if self.hold<0:
            self.hold = 0
        
        
    def draw(self):
        self.screen.blit(self.image, self.rect)
        if self.active==1:
            pygame.draw.rect(self.screen, (255,255,255),self.rect, 2)


class Bgm(pygame.sprite.Sprite):
        def __init__(self, BGM):
            pygame.sprite.Sprite.__init__(self)
            self.BGM = BGM
            self.delay = 0
            self.rect = self.image.get_rect()
            self.rect1 = self.image1.get_rect()
            self.rect.centerx = int(SCR_RECT.width*7/8)
            self.rect.centery = int(SCR_RECT.height*7/8)
            self.rect1.bottom = self.rect.top - int(SCR_RECT.height/18)
            self.rect1.centerx = self.rect.centerx
            self.g = 0.4
            self.time = 0
            self.v_init = -4
        
        def update(self):
            #jump
            self.v = int(self.v_init + self.time*self.g)
            self.rect.move_ip(0,self.v)
            self.time += 1
            if self.v==-self.v_init:
                self.time = 0
            
            
            if self.delay==0:
                pk = pygame.key.get_pressed()
                if pk[K_b]:
                    if self.BGM:
                        self.BGM = 0
                    else:
                        self.BGM = 1
                self.delay = 3
            self.delay -= 1
            if self.delay<0:
                self.delay = 0
        
        def draw(self):
            self.screen.blit(self.image, self.rect)
            if self.BGM:
                self.screen.blit(self.image1, self.rect1)
            
            
    


class Tile(pygame.sprite.Sprite):
    #色塗りタイルクラス
    #３種類のタイルを保持
    #x,yはタイルの中心座標
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.flag = 0 #tiles0グループ
        
    def change_to_1(self):
        self.hit_sound.play()
        self.image = self.image1   

    def change_to_2(self):
        self.hit_sound.play()
        self.image = self.image2



class Player(pygame.sprite.Sprite):
    #自機
    speed = SPEED
    reload_time = RELOAD
    supply_time = 30 #second弾補給まで
    change_time = 5 #second 方向変わるタイミング
    def __init__(self, flag, player_id, camera_id, auto=False):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.flag = flag
        #カメラから座標取得
        self.coord = Coordinates(player_id, camera_id)
        if self.flag==1:
            self.stick = self.stick1
            self.image = self.image1
            self.rect = self.image.get_rect()
            self.rect.center = (int(SCR_RECT.width/7),SCR_RECT.centery)
        elif self.flag==2:
            self.stick = self.stick2
            self.image = self.image2
            self.rect = self.image.get_rect()
            self.rect.center = (int(SCR_RECT.width*6/7),SCR_RECT.centery)
        #auto
        self.auto = auto
        self.auto_flag = 60*self.change_time
        self.vx = random.choice((-self.speed,self.speed))
        self.vy = random.choice((-self.speed,self.speed))
        self.reload_timer = 10
        self.supply_timer = self.supply_time*30
        self.my_tile = 0
        self.gauge = 0
        self.sp_flag = 0 #ゲージたまったらフラグが立つ

    #自分のタイルの数をカウントして保持
    def count_tiles(self):
        if self.flag==1:
            num = len(list(self.tiles1))
        elif self.flag==2:
            num = len(list(self.tiles2))
        return num

    #敵のタイルの数をカウント
    def enemy_tiles(self):
        if self.flag==1:
            num = len(list(self.tiles2))
        elif self.flag==2:
            num = len(list(self.tiles1))
        return num
    
    #camera_mode_shotはstick_mode_shotと共通
    def camera_mode_move(self):
        co = self.coord.get()
        if not co==False:
            self.rect.centerx = int(co[0]*SCR_RECT.width)
            self.rect.centery = int(co[1]*SCR_RECT.height)
        else:
            pass
    
    def auto_mode_move(self):
    
        self.rect.move_ip(self.vx, self.vy)
        if self.rect.left < 0 or self.rect.right > SCR_RECT.width:
            self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > SCR_RECT.height:
            self.vy = -self.vy
        #self.auto_flag -= 1
        #if self.auto_flag==0:
        #    self.vx = random.choice((-self.speed,self.speed))
        #    self.vy = random.choice((-self.speed,self.speed))
        #    self.auto_flag = 60*self.change_time
        #画面からはみ出ない
        self.rect = self.rect.clamp(SCR_RECT)
        
    def auto_mode_shot(self):
        pressed_keys = pygame.key.get_pressed()
        if  self.supply_timer>0:
            if pressed_keys[K_1] and self.flag==1:
                if self.sp_flag:
                    self.special()
            elif pressed_keys[K_2] and self.flag==2:
                if self.sp_flag:
                    self.special()
                
            if self.reload_timer>0:
                pass
            else:
                direction = random.choice(("up","down", "left", "right"))
                Shot(self.rect.center, direction, self.flag)        
                self.reload_timer = self.reload_time
        
        elif self.supply_timer<=0:
            if pressed_keys[K_F1] and self.flag==1:
                self.supply_timer = 30*self.supply_time
            elif pressed_keys[K_F2] and self.flag==2:
                self.supply_timer = 30*self.supply_time
        self.supply_timer -= 1
        
    def stick_mode_move(self):
        #special
        if self.stick.get_button(7) and self.sp_flag:
            self.special()
        #押されているキーに応じてプレイヤーを移動
        if self.stick.get_button(15):
            self.vx = -self.speed
        elif not self.stick.get_button(15) and self.vx==-self.speed:
            self.vx = 0
        
        if self.stick.get_button(13):
            self.vx = self.speed
        elif not self.stick.get_button(13) and self.vx==self.speed:
            self.vx = 0
        
        if self.stick.get_button(12):
            self.vy = -self.speed
        elif not self.stick.get_button(12) and self.vy==-self.speed:
            self.vy = 0
        
        if self.stick.get_button(14):
            self.vy = self.speed
        elif not self.stick.get_button(14) and self.vy==self.speed:
            self.vy = 0
        
        self.rect.move_ip(self.vx, self.vy)
        self.rect.clamp_ip(SCR_RECT)
    
    def stick_mode_shot(self):
        
        #ミサイルの発射
        if any([self.stick.get_button(m) for m in [0,1,2,3]]):
            #リロード時間が0nになるまで再発射できない
            if self.reload_timer > 0:
                pass
            else:
                #発射
                if self.stick.get_button(0):
                    Shot(self.rect.center, "up", self.flag)
                    self.reload_timer = self.reload_time
                elif self.stick.get_button(3):
                    Shot(self.rect.center, "left", self.flag)
                    self.reload_timer = self.reload_time
                elif self.stick.get_button(2):
                    Shot(self.rect.center, "down", self.flag)
                    self.reload_timer = self.reload_time
                elif self.stick.get_button(1):
                    Shot(self.rect.center, "right", self.flag)
                    self.reload_timer = self.reload_time
        
       
    
    def keyboad_mode(self):
        #押されているキーに応じてプレイヤーを移動
        pressed_keys = pygame.key.get_pressed()
        L = pressed_keys[K_LEFT]
        R = pressed_keys[K_RIGHT]
        U = pressed_keys[K_UP]
        D = pressed_keys[K_DOWN]
        
        #special
        if pressed_keys[K_j] and self.sp_flag :
            self.special()

        if L:
            self.vx = -self.speed
        elif not L and self.vx==-self.speed:
            self.vx = 0
        if R:
            self.vx = self.speed
        elif not R and self.vx==self.speed:
            self.vx = 0
        if U:
            self.vy = -self.speed
        elif not U and self.vy==-self.speed:
            self.vy = 0
        if D:
            self.vy = self.speed
        elif not D and self.vy==self.speed:
            self.vy = 0
        
        #ミサイルの発射
        if any([pressed_keys[m] for m in [K_a,K_d,K_w,K_s]]):
            #リロード時間が0nになるまで再発射できない
            if self.reload_timer > 0:
                pass
            else:
                #発射
                if pressed_keys[K_w]:
                    Shot(self.rect.center, "up", self.flag)
                    self.reload_timer = self.reload_time
                elif pressed_keys[K_a]:
                    Shot(self.rect.center, "left", self.flag)
                    self.reload_timer = self.reload_time
                elif pressed_keys[K_s]:
                    Shot(self.rect.center, "down", self.flag)
                    self.reload_timer = self.reload_time
                elif pressed_keys[K_d]:
                    Shot(self.rect.center, "right", self.flag)
                    self.reload_timer = self.reload_time
        
        self.rect.move_ip(self.vx, self.vy)
        self.rect.clamp_ip(SCR_RECT)
    
    #スペシャル攻撃
    def special(self):
        #サポートを3つ生み出す
        self.special_sound.play()
        for i in range(3):
            Support(self.rect.centerx, self.rect.centery, self.flag)
        #ゲージリセット
        self.gauge = 0
        self.sp_flag = 0
        if self.flag==1:
            self.image = self.image1
        elif self.flag==2:
            self.image = self.image2
    
    def gauge_bar(self):
        #ゲージ
        if self.gauge>SP_POINT:
            self.gauge = SP_POINT
        height = int((SCR_RECT.height*10/12)*self.gauge/SP_POINT)
        width = int(TILE_W/2)
        pos = Rect(SCR_RECT.x, SCR_RECT.y, width, height)
        pos.bottom = int(SCR_RECT.bottom*14/15)
        if self.flag==1:
            pos.left = int(SCR_RECT.width/30)
        elif self.flag==2:
            pos.right = int(SCR_RECT.width*29/30)
        
        if self.gauge==SP_POINT:
            pygame.draw.rect(self.screen, (255,0,0), pos)
        else:
            pygame.draw.rect(self.screen, (0,255,0), pos)
    
    def gauge_update(self):
        #ゲージ管理
        now_tile = self.count_tiles()
        #前と比較して増分
        gain = now_tile - self.my_tile
        if gain>0:
            self.gauge += gain
        if self.gauge==SP_POINT:
            if self.flag==1:
                self.image = self.sp_image1
            elif self.flag==2:
                self.image = self.sp_image2
            if self.sp_flag==0:
                self.gauge_sound.play()
            self.sp_flag = 1            
        self.my_tile = now_tile
        self.gauge_bar()
    
    def update(self):
        self.gauge_update()
        #self.keyboad_mode()
        self.camera_mode_move()
        self.auto_mode_shot()
        self.reload_timer -= 1

class Shot(pygame.sprite.Sprite):
    #発射する液体クラス
    speed = SHOT_SPEED #移動速度
    life = SHOT_LIFE #second 寿命 
    def __init__(self, pos, direct, flag):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.direct = direct
        self.life_time = 60*self.life
        if flag==1:
            self.shots1.add(self)
        elif flag==2:
            self.shots2.add(self)
        
    def update(self):
        if self.direct == "up":
            self.rect.move_ip(0, -self.speed)
            if self.rect.top < 0:
                self.kill()
        elif self.direct == "left":
            self.rect.move_ip(-self.speed, 0)
            if self.rect.left < 0:
                self.kill()
        elif self.direct == "down":
            self.rect.move_ip(0, self.speed)
            if self.rect.bottom > SCR_RECT.bottom:
                self.kill()
        elif self.direct == "right":
            self.rect.move_ip(self.speed, 0)
            if self.rect.right > SCR_RECT.right:
                self.kill()
        
        self.life_time -= 1
        if self.life_time==0:
            self.kill()

class Item(pygame.sprite.Sprite):
    #サポートキャラを生むアイテム
    #x,yは中心座標
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.born_sound.play()

    def generate(self, flag):
        for i in range(2):
            Support(self.rect.centerx, self.rect.centery, flag)
        
    #playerに接触したかどうか
    def collision(self):
        players_list = list(self.players)
        random.shuffle(players_list) #同時接触したとき、公平を期すため       
        for player in players_list:
            if self.rect.colliderect(player.rect):
                return True, player.flag
        return False, 0
        
    def update(self):
        bool, flag = self.collision()
        if bool:
            self.generate_sound.play()
            self.generate(flag)
            self.kill()
        
    
    
class Support(pygame.sprite.Sprite):
    #サポートキャラ
    #x,yは中心座標
    speed = SUPP_SPEED
    life = 60*SUPP_LIFE
    def __init__(self, x, y, flag):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.flag = flag #１か２
        if self.flag==1:
            self.image = self.image1
        elif self.flag==2:
            self.image = self.image2

        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.vx = random.choice((-self.speed, self.speed))
        self.vy = random.choice((-self.speed, self.speed))
        #self.vx = random.choice(range(-2*self.speed,2*self.speed+1))
        #self.vy = random.choice(range(-2*self.speed,2*self.speed+1))
        #self.tiles01 = tuple(self.tiles0) + tuple(self.tiles1)
        #self.tiles02 = tuple(self.tiles0) + tuple(self.tiles2)
    
    #x方向衝突判定
    def collision_x(self):
        #キャラのサイズ
        width = self.rect.width
        height = self.rect.height
        
        #x方向の移動先の座標と矩形を求める
        newx = self.rect.x + self.vx
        newrect = Rect(newx, self.rect.y, width, height)
        #x方向に自分の属性と異なるタイルとぶつかったとき
        if self.flag==1:
            tiles = tuple(self.tiles0) + tuple(self.tiles2)
            for tile in tiles:
                collide = newrect.colliderect(tile.rect)
                if collide:
                    change_tile_group(self.tiles0, self.tiles1, self.tiles2, tile, 1)
                    self.vx = -self.vx
                    break
            
        elif self.flag==2:
            tiles = tuple(self.tiles0) + tuple(self.tiles1)
            for tile in tiles:
                collide = newrect.colliderect(tile.rect)
                if collide:
                    change_tile_group(self.tiles0, self.tiles1, self.tiles2, tile, 2)
                    self.vx = -self.vx
                    break
        
    #y方向衝突判定
    def collision_y(self):
        #キャラのサイズ
        width = self.rect.width
        height = self.rect.height
        
        #y方向の移動先の座標と矩形を求める
        newy = self.rect.y + self.vy
        newrect = Rect(self.rect.x, newy, width, height)
        #y方向に自分の属性と異なるタイルとぶつかったとき
        if self.flag==1:
            tiles = tuple(self.tiles0) + tuple(self.tiles2)
            for tile in tiles:
                collide = newrect.colliderect(tile.rect)
                if collide:
                    change_tile_group(self.tiles0, self.tiles1, self.tiles2, tile, 1)
                    self.vy = -self.vy
                    break
                
        elif self.flag==2:
            tiles = tuple(self.tiles0) + tuple(self.tiles1)
            for tile in tiles:
                collide = newrect.colliderect(tile.rect)
                if collide:
                    change_tile_group(self.tiles0, self.tiles1, self.tiles2, tile, 2)
                    self.vy = -self.vy
                    break

    def bomb(self):
        for i in ["up", "left", "down", "right"]:
            Shot(self.rect.center, i, self.flag)
    
    def mutate(self):
        Support(self.rect.centerx, self.rect.centery, random.choice((1,2)))
    
    def toItem(self):
        Item(self.rect.centerx, self.rect.centery)
    
    def double(self):
        for i in range(2):
            Support(self.rect.centerx, self.rect.centery, self.flag)
    
    def warp(self):
        tiles = tuple(self.tiles0) + tuple(self.tiles1) + tuple(self.tiles2)
        tile = random.choice(tiles)
        Support(tile.rect.centerx, tile.rect.centery, self.flag)
        
    def update(self):
        self.collision_x()
        self.collision_y()
        
        self.rect.move_ip(self.vx, self.vy)
        if self.rect.left < 0 or self.rect.right > SCR_RECT.width:
            self.vx = -self.vx
        if self.rect.top < 0 or self.rect.bottom > SCR_RECT.height:
            self.vy = -self.vy
        #画面からはみ出ない
        self.rect = self.rect.clamp(SCR_RECT)
        
        self.life -= 1
        if self.life==0:
            self.vanish_sound.play()
            self.bomb()
            self.kill()
                
        