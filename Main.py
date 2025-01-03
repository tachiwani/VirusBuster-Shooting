import pyxel
import Character as chara

WIDTH = 192
HEIGHT = 128
ENEMY_INTERVAL = 15
ATTACK_INTERVAL = 50

class App:

    def __init__(self):
        self.game_status = 0 #0は難易度選択画面　1はゲーム画面
        self.difficulty = 0 #0はeasy 1はnomal 2はhard

        pyxel.init(WIDTH, HEIGHT)
        pyxel.load('Characters.pyxres')

        self.player = chara.Player(0,0)
        self.boss = chara.Boss(64)
        self.enemies = [] #敵リスト
        self.bullets = [] #弾のリスト
        self.attacks = [chara.BossAttack()] #攻撃エフェクトのリスト
        self.enemy_interval = ENEMY_INTERVAL
        self.attack_interval = ATTACK_INTERVAL
        self.cnt_enemy = 0
        self.cnt_attack = 0
        self.is_game_over = False
        self.is_clear = False
        self.score = 0
        self.pointer_y = 48.5 #難易度選択のポインタ位置

        pyxel.run(self.update,self.draw)

    def reset(self): #ゲームをリセット
        self.player = chara.Player(0,0)
        self.boss = chara.Boss(64)
        self.enemies = [] #敵リスト
        self.bullets = [] #弾のリスト
        self.attacks = [chara.BossAttack()] #攻撃エフェクトのリスト
        self.enemy_interval = ENEMY_INTERVAL
        self.attack_interval = ATTACK_INTERVAL
        self.cnt_enemy = 0
        self.cnt_attack = 0
        self.is_game_over = False
        self.is_clear = False
        self.score = 0
        self.pointer_y = 48.5 #難易度選択のポインタ位置


    def update(self):
        if self.game_status == 0:
            self.update_standby()
        elif self.game_status == 1:
            self.update_game()

    def update_standby(self):
        #難易度選択画面

        if self.difficulty <= 0:
            self.difficulty =0

        if self.difficulty >= 2:
            self.difficulty = 2

        if self.pointer_y <= 48.5:
            self.pointer_y = 48.5

        if self.pointer_y >= 68.5:
            self.pointer_y = 68.5

        #操作
        if pyxel.btnp(pyxel.KEY_UP):
            self.difficulty -= 1
            self.pointer_y -= 10
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.difficulty += 1
            self.pointer_y += 10

        if pyxel.btnp(pyxel.KEY_RETURN or pyxel.KEY_SPACE):
            self.game_status = 1 

    def update_game(self):
        #難易度調整
        if self.difficulty == 0:
            self.enemy_interval = 30
            self.attack_interval = 90
            for attack in self.attacks:
                attack.speed = 0.3

        elif self.difficulty == 2:
            self.enemy_interval = 8
            self.attack_interval = 20
            for attack in self.attacks:
                attack.speed = 0.8

        for attack in self.attacks:
            print(attack.speed)

        #プレイヤーの更新
        self.player.update(self.bullets)
        #枠外に行かないようにする
        if self.player.y >= HEIGHT - 16:
            self.player.y = HEIGHT - 16
        if self.player.y <= 0:
            self.player.y = 0
        if self.player.x >= WIDTH:
            self.player.x = WIDTH
        if self.player.x <= 0:
            self.player.x = 0
        

        #タイマーが一定時間経過したら敵を生成
        if self.checkTimer() == True :
            self.makeEnemy()
        
        #タイマーが一定時間経過したら攻撃を生成
        if self.attackCheckTimer() == True:
            self.makeAttack()

        #ボスの更新
        self.boss.update()

        #敵の更新
        for enemy in self.enemies:
            enemy.update(self.player)

        #攻撃の更新
        for attack in self.attacks:
            attack.update(self.player)

        #弾の更新
        for bullet in self.bullets:
            bullet.update()

        #プレイヤーの生存判定
        if not self.player.is_alive:
            self.is_game_over = True

        #ボスの生存判定
        if not self.boss.is_alive:
            self.is_alive = False

        #生存していない攻撃を削除
        for attack in self.attacks[:]:
            if not attack.is_alive:
                self.attacks.remove(attack)
        
        # 生存していない敵を削除
        for enemy in self.enemies[:]:  # リスト全体のコピーをイテレート
            if not enemy.is_alive:    # 生存していない場合消す
                self.enemies.remove(enemy)

        # 生存していない弾丸を削除
        for bullet in self.bullets:  # リスト全体のコピーをイテレート
            if not bullet.is_alive:     # 生存していない場合消す
                self.bullets.remove(bullet)

        # 生存していない攻撃を削除
        for attack in self.attacks:  # リスト全体のコピーをイテレート
            if not attack.is_alive:     # 生存していない場合消す
                self.attacks.remove(attack)


        #当たり判定で削除予定の弾丸と敵の入れる専用のリスト
        bullets_to_remove = []
        enemies_to_remove = []

        # 弾と敵の当たり判定
        for bullet in self.bullets[:]:  # リストのコピーをイテレート
            for enemy in self.enemies[:]:
                if self.checkHit(bullet, enemy):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    if (not self.is_game_over and not self.is_clear):
                        self.score += 1

        # 弾とボスの当たり判定
        for bullet in self.bullets[:]:  # リストのコピーをイテレート
            if self.checkHit(bullet, self.boss):
                print("ボスに当たった") #デバッグ用
                self.boss.ani_flg = True
                if (not self.is_game_over and not self.is_clear):
                     self.score += 1

        #当たり判定済の弾丸と敵を削除
        for bullet in bullets_to_remove:
            if bullet in self.bullets:  # リストにまだ存在している場合に削除
                self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            if enemy in self.enemies:  # リストにまだ存在している場合に削除
                self.enemies.remove(enemy)

        #プレイヤーと敵の当たり判定
        if not self.is_game_over or self.is_clear:
            for enemy in self.enemies:
                if self.checkHit(self.player,enemy):
                    self.player.ani_flg = True

        #プレイヤーと攻撃の当たり判定
        if not self.is_game_over or self.is_clear:
            for attack in self.attacks:
                self.checkHit(self.player,attack)

        #攻撃と弾の当たり判定
        for bullet in self.bullets:
            for attack in self.attacks:
                self.checkHit(bullet,attack)

        #クリア判定
        if self.boss.is_alive == False:
            self.is_clear = True

        #ゲームオーバー/クリア後のやり直し
        if self.is_game_over or self.is_clear:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset()
                self.game_status = 0

    def makeEnemy(self):
        if not self.is_clear or self.is_game_over:
            self.enemies.append(chara.Enemy(self.boss))

    def makeAttack(self):
        if not self.is_clear or self.is_game_over:
            self.attacks.append(chara.BossAttack())

    def checkTimer(self):  #敵発生用のタイマー
        #一定時間でTrueを返す
        bRet = False
        self.cnt_enemy = (self.cnt_enemy + 1) % self.enemy_interval
        if(self.cnt_enemy == 0):
            bRet = True
        return bRet
    
    def attackCheckTimer(self, interval = ATTACK_INTERVAL):  #ボスの攻撃エフェクト発生用のタイマー
        #一定時間でTrueを返す
        bRet = False
        self.cnt_attack = (self.cnt_attack + 1) % interval
        if(self.cnt_attack == 0):
            bRet = True
        return bRet
    
    #当たり判定の抽象メソッド
    def checkHit(self,a,b):
        if (a.x < b.x + b.w and
            a.x + a.w > b.x and
            a.y < b.y + b.h and
            a.y + a.h > b.y):
                    a.hp -= 1  # aのHPを-1
                    b.hp -= 1  # bのHPを-1
                    return True #当たったらTrue
        return False #当たらなかったらFalse

    def draw(self):
        if self.game_status == 0:
            self.draw_standby()
        elif self.game_status == 1:
            self.draw_game()

    def draw_standby(self):
        pyxel.cls(0)
        pyxel.text(70, 30, "VIRUS BUSTER", pyxel.frame_count % 16)
        pyxel.text(65, 45, "SELECT DIFFICULTY", 6)
        pyxel.blt(50, self.pointer_y, 0, 32, 0, 16, 16, 0) #ポインタ
        pyxel.text(70, 55, "EASY", 6)
        pyxel.text(70, 65, "NOMAL", 6)
        pyxel.text(70, 75, "HARD", 6)
        pyxel.text(45, 100, "PRESS ENTER START", 6)
        
    def draw_game(self):
        pyxel.cls(0)
        
        pyxel.bltm(0, 0, 0, 0, 0, WIDTH, HEIGHT)

        # ゲームオーバー時の画面描画
        if self.is_game_over:
            pyxel.cls(5)
            pyxel.text(76, 55, "GAME OVER", pyxel.frame_count % 16)
            your_score = "YOUR SCORE IS " + str(self.score)
            pyxel.text(64, 65, your_score, pyxel.frame_count % 16)
            pyxel.text(50, 110, "YOUR SECURITY IS LOST...", 0)
            pyxel.text(50, 120, "PRESS ENTER TO RESTART", 7)
            return #これ以降の処理を行わない　画面を止める
        
        #クリア時の画面描画
        if self.is_clear:
            pyxel.cls(5)
            pyxel.text(76, 55, "GAME CLEAR!", pyxel.frame_count % 16)
            your_score = "YOUR SCORE IS " + str(self.score)
            pyxel.text(64, 65, your_score, pyxel.frame_count % 16)
            pyxel.text(50, 110, "PRIVACY IS PROTECTED!", 7)
            pyxel.text(50, 120, "PRESS ENTER TO RESTART", 7)
            return #これ以降の処理を行わない
        
        #プレイヤの描画
        self.player.draw()
        
        #攻撃の描画
        for attack in self.attacks:
            i=0
            for i in range(0, 20, 4): # 0から20まで4ずつ下にずらして描画（4回ループ）
                attack.draw(i)

        #敵の描画
        for enemy in self.enemies:
            enemy.draw()  

        #ボスの描画
        self.boss.draw()
        
        #プレイヤの描画
        self.player.draw()

        #弾の描画
        for bullet in self.bullets:
            bullet.draw()

        # ボスのHPゲージ描画
        boss_hp_ratio = self.boss.hp / self.boss.max_hp  # HPの割合を計算
        bar_width = 100  # ゲージの幅
        bar_height = 4   # ゲージの高さ
        bar_x = (WIDTH - bar_width) // 2  # 中央に配置
        bar_y = 0  # 画面上部から10px下
        # ゲージの背景（灰色）
        pyxel.rect(bar_x, bar_y, bar_width, bar_height, 13)  # バーの背景
        # ゲージの現在値（赤色）
        pyxel.rect(bar_x, bar_y, int(bar_width * boss_hp_ratio), bar_height, 8)  # HPバー
        pyxel.text(10, 0,"BOSS HP:",1)

        #スコアを表示
        score_now = "score: " + str(self.score)
        pyxel.text(150,0,score_now,1)

        #プレイヤーのHPを表示
        hp_now = "." * self.player.hp
        pyxel.text(170,120,hp_now,1)
        pyxel.text(130,120,"PLAYER HP:",1)

        
App()