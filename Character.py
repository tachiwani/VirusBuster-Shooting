import pyxel
import random

PLAYER_IMG_NO = 0
ENEMY_IMG_NO = 1
PLAYER_SPEED = 2
PLAYER_X = 56
PLAYER_Y = 105
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16
PLAYER_V = 16
PLAYER_HP = 5


class Player:

    ani_no = 0 #ドット絵のナンバー
    enemies = [] #敵を入れる箱(配列)

    def __init__(self,x,y):
        self.x = PLAYER_X
        self.y = PLAYER_Y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.hp = PLAYER_HP
        self.is_alive = True
        self.ani_flg = False
        self.ani_cnt = 0
        self.ani_max = 10 #被弾時の点滅回数
    
    def update(self, bullets):

        #ボタン操作　上下左右
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.y -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.y += PLAYER_SPEED

        #消滅判定
        if (self.hp <= 0):
            self.is_alive = False

        #弾の発射
        if pyxel.btnp(pyxel.KEY_SPACE):
            bullets.append(Bullet(self.x, self.y))

        #被弾時の点滅アニメーション
        if self.ani_flg:
            self.ani_cnt += 1
            if self.ani_cnt >= self.ani_max:
                self.ani_flg = False
                self.ani_cnt = 0 #カウンターをリセット

    def draw(self):
        if self.ani_flg and self.ani_cnt % 2 == 0:
            pyxel.blt(self.x, self.y, PLAYER_IMG_NO, 16, 0, 16, 16, 0)
        else:
            pyxel.blt(self.x, self.y, PLAYER_IMG_NO, 0, 0, 16, 16, 0)



ENEMY_X = 0
ENEMY_Y = 0
ENEMY_W = 16
ENEMY_V = 16
ENEMY_SPEED = 1.2
ENEMY_HP = 1
ENEMY_WIDTH = 16
ENEMY_HEIGHT = 16

class Enemy:

    ani_no = 1 #ドット絵のナンバー

    def __init__(self,boss):
        self.x = boss.x #ボスから発射
        self.y = ENEMY_Y
        self.hp = ENEMY_HP
        self.h = ENEMY_HEIGHT
        self.w = ENEMY_WIDTH
        self.is_alive = True

    def update(self,player):
        self.y += ENEMY_SPEED
        if (self.x == player.x):
            self.x = player.x
        elif (self.x > player.x):
            self.x -= ENEMY_SPEED
        elif (self.x < player.x):
            self.x += ENEMY_SPEED

        #消滅判定
        if (self.hp <= 0):
            self.is_alive = False

    def draw(self):
        pyxel.blt(
            self.x, self.y, 
            ENEMY_IMG_NO,
            0, 16, 
            16, 16, 
            0)


BOSS_Y = 4
BOSS_WIDTH = 32
BOSS_HEIGHT = 32
BOSS_SPEED = 3
BOSS_HP = 20

class Boss:

    def __init__(self,x):
        self.x = x
        self.y = BOSS_Y
        self.w = BOSS_WIDTH
        self.h = BOSS_HEIGHT
        self.s = BOSS_SPEED
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.is_alive = True
        self.ani_flg = False
        self.ani_cnt = 0
        self.ani_max = 10 #被弾時の点滅回数

    def update(self):
        self.x += self.s
        if (self.x >= 168 or self.x <= 0):
            self.s *= -1

        #消滅判定
        if (self.hp <= 0):
            self.is_alive = False

        if self.ani_flg:
            self.ani_cnt += 1
            if self.ani_cnt >= self.ani_max:
                self.ani_flg = False
                self.ani_cnt = 0 #カウンターをリセット

    def draw(self):
        #点滅時
        if self.ani_flg and self.ani_cnt % 2 == 0 : #2フレーム間隔で点滅
            pyxel.blt(
                self.x, self.y,  # 描画位置
                ENEMY_IMG_NO,  # .pyxres の画像番号
                0, 64,  # 切り出し(x,y) 透明
                self.w, self.h,  # スプライトの幅と高さ
                0  # 透過色なし
                )   

        #通常時
        else:
            pyxel.blt(
                self.x, self.y,  # 描画位置
                ENEMY_IMG_NO,  # .pyxres の画像番号
                0, 32,  # 切り出し(x,y)
                self.w, self.h,  # スプライトの幅と高さ
                0  # 透過色なし
                )   
            
        
ATTACK_Y = -24
ATTACK_WIDTH = 36
ATTACK_HEIGHT = 16
ATTACK_HP = 1
ATTACK_SPEED = 0.4

class BossAttack:

    def __init__(self):
        self.x = random.randint(0,168)
        self.y = ATTACK_Y
        self.w = ATTACK_WIDTH
        self.h = ATTACK_HEIGHT
        self.hp = ATTACK_HP
        self.speed = ATTACK_SPEED
        self.is_alive = True

    def update(self, player):
        self.y += self.speed
        if self.y > pyxel.height:
            self.is_alive = False
            player.is_alive = False

        #消滅判定
        if (self.hp <= 0):
            self.is_alive = False

    def draw(self, i):
        pyxel.blt(
            self.x + i, self.y + i,
            ENEMY_IMG_NO,
            0, 0, 
            self.w, self.h, 
            0)


        
BULLET_SPEED = 5  # 弾のスピード
BULLET_IMG_NO = 2  # .pyxres の画像番号
BULLET_U = 0  # スプライトの u 座標
BULLET_V = 0  # スプライトの v 座標
BULLET_WIDTH = 16  # 弾の幅
BULLET_HEIGHT = 16  # 弾の高さ
BULLET_HP = 1

class Bullet:

    def __init__(self, x, y):
        self.speed = BULLET_SPEED
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.hp = BULLET_HP
        self.is_alive = True

    def update(self):
        self.y -= self.speed
        if self.y < 0:
            self.is_alive = False

        #消滅判定
        if (self.hp <= 0):
            self.is_alive = False
        
    def draw(self):
        pyxel.blt(
            self.x, self.y,  # 描画位置
            BULLET_IMG_NO,  # .pyxres の画像番号
            BULLET_U, BULLET_V,  # スプライトの座標
            self.w, self.h,  # スプライトの幅と高さ
            0  # 透過色なし
            )