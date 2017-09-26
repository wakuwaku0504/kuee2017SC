# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 22:11:17 2017

@author: TE058
"""
import pygame
import sys
import cv2
import random
from pygame.locals import *

from tools import *
from sprites import *
from teams import *

START, WAIT, PRE, PLAY, GAME_SET, SCORE, CONFIG = (0, 1, 2, 3, 4, 5, 6) 

FULL = 1
BGM = 0
#チーム設定
P1 = player1
P2 = player2

ID1 = 3 #1pのid
ID2 = 4 #2pのid
CAM1 = 0
CAM2 = 2
TEAMS = [player1, player2]


class jintori(object):
    def __init__(self):
        self.stick1 = joystick(1) #joystick instance
        self.stick2 = joystick(2)
        #player割り当て
        self.P1 = P1
        self.P2 = P2
        self.BGM = BGM
        pygame.init()
        pygame.mixer.init()
        if FULL:
            self.screen = pygame.display.set_mode((SCR_RECT.width,SCR_RECT.height), FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCR_RECT.width,SCR_RECT.height))
        pygame.display.set_caption("Demo")
    
        #イメージを用意
        #サムネ
        self.teams_thumb = [load_image(m.image, 3*TILE_W, 3*TILE_H) for m in TEAMS]
        self.load_img()
        #サウンドを用意
        self.load_snd()
        #ゲームオブジェクトを初期化
        self.init_game()
    
        clock = pygame.time.Clock()

        while(1):
            clock.tick(FPS) #40fps
            self.screen.blit(self.backImg,(0,0))
            self.update()
            self.draw( )
            pygame.display.update()
            self.key_handler()
            
    def bgm_play(self):
        #BGM再生
        if self.BGM:
            n = random.choice(range(1,10))
            pygame.mixer.music.load("sound/bgm{}.mp3".format(n))
            pygame.mixer.music.play(-1)
        
    def config_bgm(self):
        if self.BGM:
            pygame.mixer.music.load("sound/config_bgm.mp3")
            pygame.mixer.music.play(-1)
        
    def extra_bgm(self):
        if self.BGM:
            if self.snd_b==0:
                pygame.mixer.music.load("sound/extra_bgm.mp3")
                pygame.mixer.music.play(-1)
                self.snd_b = 1
    
    def score_bgm(self):
        if self.BGM:
            if self.snd_b==0:
                n = random.choice((1,2,3))
                pygame.mixer.music.load("sound/score_loop{}.mp3".format(n))        
                pygame.mixer.music.play(-1)
                self.snd_b = 1
            
    def reflect_config(self):
        self.P1, self.P2 = self.card.players()
    
    #ゲーム内のフラグ、数値初期化
    def init_flags(self):
        #ゲーム状態
        self.game_state = START
        #ゲーム残り時間
        self.limite = 60*LIMITE
        #4０周するとたつ
        self.loop = 0
        #アイテム発生用
        self.flag_item = True
        self.item_time = ITEM_TIME
        #スコア遅延用
        self.accum = 0
        #スコア発表用
        self.snd = 0
        #bgm一回だけ鳴らすため
        self.snd_b = 0
        #extra突入フラグ
        self.extra = False
        #タイル配置用
        self.SCR_CX = SCR_RECT.centerx
        self.SCR_CY = SCR_RECT.centery
        self.tile_rangex1 = range(self.SCR_CX+2*TILE_W, SCR_RECT.right-TILE_W, TILE_W) #真ん中から右
        self.tile_rangex2 = range(self.SCR_CX-2*TILE_W, TILE_W, -TILE_W)      #真ん中から左
        self.tile_rangey1 = range(self.SCR_CY, SCR_RECT.bottom-TILE_H, TILE_H)#真ん中から下
        self.tile_rangey2 = range(self.SCR_CY-TILE_H, TILE_H, -TILE_H)      #真ん中から上
    
        
        
    def init_tiles(self):
        #タイルを作成
        for i in self.tile_rangex1:
            for j in self.tile_rangey1:
                Tile(i,j)
            for j in self.tile_rangey2:
                Tile(i,j)
        
        for i in self.tile_rangex2:
            for j in self.tile_rangey1:
                Tile(i,j)
            for j in self.tile_rangey2:
                Tile(i,j)
        
        for i in range(self.SCR_CX-TILE_W, self.SCR_CX+2*TILE_W, TILE_W):
            for j in range(self.SCR_CY+TILE_H, SCR_RECT.bottom-TILE_H, TILE_H):
                Tile(i,j)
                
        for i in range(self.SCR_CX-TILE_W, self.SCR_CX+2*TILE_W, TILE_W):
            for j in range(self.SCR_CY-TILE_H, TILE_H, -TILE_H):
                Tile(i,j) 
    
    def init_game(self):
        #ゲームオブジェクト初期化
        self.init_flags()
        self.card = Card(Thumbnail(), Thumbnail(),self.screen, self.teams_thumb)
        self.bgm = Bgm(self.BGM) 
        
        #スプライトグループを作成して登録
        self.all = pygame.sprite.RenderUpdates()
        self.players = pygame.sprite.Group()
        self.tiles0 = pygame.sprite.Group() #中立タイルグループ
        self.tiles1 = pygame.sprite.Group() #1側タイル
        self.tiles2 = pygame.sprite.Group() #2側タイル
        self.shots1 = pygame.sprite.Group()
        self.shots2 = pygame.sprite.Group()
        self.supports = pygame.sprite.Group()
    
        Player.containers = self.all, self.players
        Shot.containers = self.all
        Tile.containers = self.all, self.tiles0
        Item.containers = self.all, self.supports
        Support.containers = self.all, self.supports
        
        Bgm.screen = self.screen
        
        Player.screen = self.screen
        Player.tiles1 = self.tiles1
        Player.tiles2 = self.tiles2
        Player.stick1 = self.stick1
        Player.stick2 = self.stick2
        
        Shot.shots1 = self.shots1
        Shot.shots2 = self.shots2
        
        Item.players = self.players
        
        Support.tiles0 = self.tiles0
        Support.tiles1 = self.tiles1
        Support.tiles2 = self.tiles2
        
        self.init_tiles()
        
        #自機を作成
        Player(1,player_id=ID1,camera_id=CAM1)
        #Player(1, 1)
        #敵機を作成
        Player(2,player_id=ID2,camera_id=CAM2)
        #Player(2, 1)
    
    def update(self):
        #ゲーム状態の更新
        if self.game_state==CONFIG:
            self.card.update()
            self.bgm.update()
            self.P1, self.P2 = self.card.players(TEAMS)
            self.BGM = self.bgm.BGM
            
        elif self.game_state==WAIT:
            for player in self.players:
                player.camera_mode_move()
        elif self.game_state==PLAY:
            #スプライトを更新
            self.all.update()
            #衝突判定
            collision_detection1(self.tiles0, self.tiles1, self.tiles2, self.shots1)
            collision_detection2(self.tiles0, self.tiles1, self.tiles2, self.shots2)
            #アイテム発生
            if self.flag_item:
                x, y = gene_item(self.tiles0, self.tiles1, self.tiles2)
                Item(x, y)
                self.flag_item = False
                self.item_time = 0
            if len(list(self.supports))==0: #supportが存在しないときにカウント     
                self.item_time += 1
                if self.item_time==FPS*ITEM_TIME:
                    self.flag_item = True
    
    def draw_title(self):
        #タイトル描画
        title_font = pygame.font.SysFont(None, 80)        
        title = title_font.render("KUEE Summer Camp 2017", False, (255,0,0))
        title_pos = ((SCR_RECT.width-title.get_width())/2,int(SCR_RECT.height/3))
        self.screen.blit(title, title_pos)
        #PUSH SPACEを描画
        push_font = pygame.font.SysFont(None, 40)
        push_space = push_font.render("PUSH SPACE KEY", False, (255,255,255))
        push_space_pos = ((SCR_RECT.width-push_space.get_width())/2, int(SCR_RECT.height/2))
        self.screen.blit(push_space, push_space_pos)
    
    def draw_config(self):
        #コンフィグ画面
        self.card.draw()
        self.bgm.draw()
    
    def draw_wait(self):
        self.all.draw(self.screen)
        m = int(self.limite / 60)
        s = self.limite % 60
        #時間描画
        rest_font = pygame.font.SysFont(None, 80)
        rest = rest_font.render('{0:02d}:{1:02d}'.format(m,s), False, (0,0,0))
        rest_pos = (
                (SCR_RECT.width-rest.get_width())/2,
                (SCR_RECT.height-rest.get_height())/2)
        self.screen.blit(rest, rest_pos)
    
    def draw_pre(self):
        self.all.draw(self.screen)
        m = int(self.limite / 60)
        s = self.limite % 60
        #時間描画
        rest_font = pygame.font.SysFont(None, 80)
        rest = rest_font.render('{0:02d}:{1:02d}'.format(m,s), False, (0,0,0))
        rest_pos = (
                (SCR_RECT.width-rest.get_width())/2,
                (SCR_RECT.height-rest.get_height())/2)
        self.screen.blit(rest, rest_pos)
    
    def draw_play(self):
        self.all.draw(self.screen)
        m = int(self.limite / 60)
        s = self.limite % 60
        #時間描画
        rest_font = pygame.font.SysFont(None, 80)
        if self.limite>10: #残り時間が10秒より残っていたら黒
            rest = rest_font.render('{0:02d}:{1:02d}'.format(m,s), False, (0,0,0))
        else:
            rest = rest_font.render('{0:02d}:{1:02d}'.format(m,s), False, (255,0,0))
        rest_pos = (
                (SCR_RECT.width-rest.get_width())/2,
                (SCR_RECT.height-rest.get_height())/2)
        self.screen.blit(rest, rest_pos)
        self.loop += 1
        if self.loop==FPS:
            self.limite -= 1
            self.loop = 0
        if self.limite==0:
            self.game_state = GAME_SET
            pygame.mixer.music.fadeout(2*1000)
        #bar image
        self.screen.blit(self.support1_icon,self.supp1_rect)
        self.screen.blit(self.support2_icon,self.supp2_rect)
        self.screen.blit(self.tama1_icon,self.tama1_rect)
        self.screen.blit(self.tama2_icon,self.tama2_rect)
            
    def draw_game_set(self):
        self.all.draw(self.screen)
        m = 0
        s = 0
        #時間描画
        rest_font = pygame.font.SysFont(None, 80)
        rest = rest_font.render('{0:02d}:{1:02d}'.format(m,s), False, (255,0,0))
        rest_pos = (
                (SCR_RECT.width-rest.get_width())/2,
                (SCR_RECT.height-rest.get_height())/2)
        self.screen.blit(rest, rest_pos)
        self.loop += 1
        if self.loop==2*FPS:
            self.loop = 0
            self.game_state = SCORE
            
    def draw_score(self):
        self.all.draw(self.screen)   
        SCORE_RECT = Rect(
                int(SCR_RECT.width/7),
                int(SCR_RECT.height/7),
                int(SCR_RECT.width*5/7),
                int(SCR_RECT.height*5/7)
                )
        #スコア背景
        self.screen.fill((0,0,0), SCORE_RECT)
        #スコアタイトル
        s_t_font = pygame.font.SysFont(None, 80)
        s_title = s_t_font.render("SCORE", False, (255,255,255))
        s_title_pos = ((SCR_RECT.width-s_title.get_width())/2, int(SCR_RECT.height*2/8))
        self.screen.blit(s_title, s_title_pos)
        #スコア計算
        score0, score1, score2 = calc_score(self.tiles0, self.tiles1, self.tiles2)
        #スコア表示
        score_font = pygame.font.SysFont(None, 90)
        scores = score_font.render(
                'Player1:{0} Player2:{1}'.format(score1, score2), False, (255,255,255))
        scores_pos = ((SCR_RECT.width-scores.get_width())/2, int(SCR_RECT.height*3/8))
        if self.accum>=FPS:
            self.screen.blit(scores, scores_pos)
        #勝者判定
        winner_font = pygame.font.SysFont(None, 150)
        if score1>score2:
            winner = winner_font.render("Player1!!", False, (255,255,255))
        elif score1<score2:
            winner = winner_font.render("Player2!!", False, (255,255,255))
        elif score1==score2:
            winner = winner_font.render("Draw", False, (255,255,255))
            self.extra = True
        winner_pos = ((SCR_RECT.width-winner.get_width())/2, int(SCR_RECT.height/2))
        if not self.extra:
            self.score_bgm()
        if self.accum>=2*FPS:
            self.screen.blit(winner, winner_pos)
            if self.extra:
                self.extra_bgm()
            if self.extra and self.accum>=4.25*FPS:
                extra_font = pygame.font.SysFont(None, 160)
                extra = extra_font.render("EXTRA!!", False, (255,255,255))
                extra_pos = ((SCR_RECT.width-extra.get_width())/2, int(SCR_RECT.height*2/3))
                self.screen.blit(extra, extra_pos)
                if self.accum>=5.7*FPS:
                    self.accum = 0
                    self.limite = 20
                    self.extra = False
                    self.snd = 0
                    self.snd_b = 0
                    self.game_state = PLAY
            else: 
                if not self.extra and self.snd==0:    
                    self.congratulations_sound.play() #一回だけ鳴らす
                    self.snd = 1
        
        self.accum += 1
        if self.accum>500:
            self.accum = 500 #カンスト防ぎ用
    
    def draw(self):
        #描画
        if self.game_state==START:
            self.draw_title()
        elif self.game_state==CONFIG:
            self.draw_config()
        elif self.game_state==WAIT:
            self.draw_wait()
        elif self.game_state==PRE:
            self.draw_pre()
        elif self.game_state==PLAY:
            self.draw_play()
        elif self.game_state==GAME_SET:
            self.draw_game_set()
        elif self.game_state==SCORE:
            self.draw_score()
    
    def key_handler(self):
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
                for player in self.players:
                    player.releas()
            elif event.type==KEYDOWN and event.key==K_ESCAPE:
                pygame.quit()
                sys.exit()
                for player in self.players:
                    player.release()
                
            elif event.type==KEYDOWN and event.key==K_c:
                if self.game_state==START:
                    self.config_bgm()
                    self.game_state = CONFIG
                elif self.game_state==CONFIG:
                    self.load_img()
                    self.init_game()
                    self.game_state = START
                    pygame.mixer.music.fadeout(1000)
            
            elif event.type==KEYDOWN and event.key==K_SPACE:
                if self.game_state==START: #スタート画面でスペースを押したとき
                    self.game_state = WAIT
                elif self.game_state==WAIT:
                    for player in self.players:
                        player.init_pos()
                    self.game_state = PRE
                elif self.game_state==PRE:
                    #self.count_sound.play()
                    #pygame.time.delay(1230)
                    self.game_state = PLAY
                    self.bgm_play()
                elif self.game_state==PLAY:
                    self.game_state = GAME_SET
                    pygame.mixer.music.fadeout(2*1000)
                elif self.game_state==GAME_SET:
                    self.game_state = SCORE
                
        
   
    def load_img(self):
        #背景イメージのロード
        self.backImg = pygame.image.load("image/sky2.jpg").convert()
        #barの下に表示する画像rect
        self.support1_icon = load_image(
                self.P1.support, int(TILE_W/2), int(TILE_H/2), colorkey=-1)
        self.support2_icon = load_image(
                self.P2.support, int(TILE_W/2), int(TILE_H/2), colorkey=-1)
        self.tama1_icon = load_image(
                "image/bulletred.png", int(TILE_W/2), int(TILE_H/2), colorkey=-1)
        self.tama2_icon = self.tama1_icon
        #rect取得
        self.supp1_rect = self.support1_icon.get_rect()  
        self.supp2_rect = self.support2_icon.get_rect()
        self.tama1_rect = self.tama1_icon.get_rect()
        self.tama2_rect = self.tama2_icon.get_rect()
        #位置合わせ
        self.supp1_rect.top = int(SCR_RECT.bottom*14/15)
        self.supp1_rect.left = int(SCR_RECT.width/30)
        self.supp2_rect.top = int(SCR_RECT.bottom*14/15)
        self.supp2_rect.right = int(SCR_RECT.width*29/30)
        self.tama1_rect.top = int(SCR_RECT.bottom*14/15)
        self.tama1_rect.right = int(SCR_RECT.width/30)
        self.tama2_rect.top = int(SCR_RECT.bottom*14/15)
        self.tama2_rect.left = int(SCR_RECT.width*29/30)
        
        #スプライトの画像を登録
        Bgm.image = load_image("image/penguin.png", int(TILE_W*1.4), int(TILE_H*2.2), colorkey=-1)
        Bgm.image1 = load_image("image/onpu.png",TILE_W, TILE_H, colorkey=-1)
        Tile.image = load_image("image/kuro.jpg", TILE_W, TILE_H, colorkey=-1)
        Tile.image1 = load_image(self.P1.tile, TILE_W, TILE_H, colorkey=-1)
        Tile.image2 = load_image(self.P2.tile, TILE_W, TILE_H, colorkey=-1)
        Player.image1 = load_image(self.P1.image, TILE_W*2, TILE_H*2, colorkey=-1)
        Player.image2 = load_image(self.P2.image, TILE_W*2, TILE_H*2, colorkey=-1)
        Player.sp_image1 = load_image(self.P1.sp_image, TILE_W*2, TILE_H*2, colorkey=-1)
        Player.sp_image2 = load_image(self.P2.sp_image, TILE_W*2, TILE_H*2, colorkey=-1)
        Shot.image = load_image("image/bulletred.png", int(TILE_W/2), int(TILE_H/2), colorkey=-1)
        Item.image = load_image("image/box.png", TILE_W, TILE_H,colorkey=-1)
        Support.image1 = load_image(self.P1.support, TILE_W, TILE_H, colorkey=-1)
        Support.image2 = load_image(self.P2.support, TILE_W, TILE_H, colorkey=-1)
        
    def load_snd(self):
        #効果音ロード
        Player.gauge_sound = pygame.mixer.Sound("sound/gauge2.wav")
        Player.special_sound = pygame.mixer.Sound("sound/special2.wav")
        Tile.hit_sound = pygame.mixer.Sound("sound/hit3.wav")
        Item.generate_sound = pygame.mixer.Sound("sound/generate.wav")
        Item.born_sound = pygame.mixer.Sound("sound/item.wav")
        Support.vanish_sound  = pygame.mixer.Sound("sound/vanish.wav")
        
        self.count_sound = pygame.mixer.Sound("sound/count.wav")
        self.congratulations_sound = pygame.mixer.Sound("sound/congratulations!.wav")
        self.extra_sound = pygame.mixer.Sound("sound/extra!!.wav")
        
def main():
    jintori()
    
if __name__ == "__main__":
    main()