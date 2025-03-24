import pygame
import random
import os

WIDTH = 500
HEIGHT = 600
TIME_UPDATE = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = ( 255, 255, 0)

#  初始化
pygame.init()


# 设置显示屏幕的比例
screen = pygame.display.set_mode((WIDTH,HEIGHT))

# 调节屏幕刷新率
clock = pygame.time.Clock()

running = True

# 获取图片
background_image = pygame.image.load(os.path.join('img','background.png')).convert()
#rock_image = pygame.image.load(os.path.join('img','rock.png')).convert()
bullet_image = pygame.image.load(os.path.join('img','bullet.png')).convert()
player_image = pygame.image.load(os.path.join('img','player.png')).convert()
rocks_image = list()
for x in range(7):
    rocks_image.append(pygame.image.load(os.path.join('img',f'rock{x}.png')).convert())
player_mini_image = pygame.transform.scale(player_image,(25,25))
player_mini_image.set_colorkey(BLACK)# 获取生命条数的飞机动画
power_image = {} # 获取宝物图片
power_image['gun'] = pygame.image.load(os.path.join('img','gun.png')).convert()
power_image['shield'] = pygame.image.load(os.path.join('img','shield.png')).convert()

# 添加音效
shoot_sound = pygame.mixer.Sound(os.path.join('sound','shoot.wav'))
expl_sound = [
pygame.mixer.Sound(os.path.join('sound','expl0.wav')),
pygame.mixer.Sound(os.path.join('sound','expl1.wav'))
]
pygame.mixer.music.load(os.path.join('sound','background.ogg'))
player_expl_sound = pygame.mixer.Sound(os.path.join('sound','rumble.ogg'))# 飞机爆炸音效
gun_sound = pygame.mixer.Sound(os.path.join('sound','pow0.wav'))
shield_sound = pygame.mixer.Sound(os.path.join('sound','pow1.wav'))

# 添加爆炸动画
# 储存照片的是列表，但是要区分子弹碰撞石头，和石头碰撞飞船的爆炸动画，因此要用字典区分
explosion_image = {}
explosion_image['lg']=[]
explosion_image['sm']=[]
explosion_image['player'] = []# 添加飞机死亡时的爆炸动画

# 更改游戏图示
pygame.display.set_icon(player_mini_image)
pygame.display.set_caption("太空生存站")
for i in range(9):
    expl_image = pygame.image.load(os.path.join('img',f'expl{i}.png')).convert()
    expl_image.set_colorkey(BLACK)
    explosion_image['lg'].append(pygame.transform.scale(expl_image,(75,75)))
    explosion_image['sm'].append(pygame.transform.scale(expl_image,(25,25)))

for i in range(9):
    player_expl_image = pygame.image.load(os.path.join('img',f'player_expl{i}.png')).convert()
    player_expl_image.set_colorkey(BLACK)
    explosion_image['player'].append(player_expl_image)


# 获取字体
#font_type = pygame.font.match_font('arial')当前字体不适用用于中文
font_type = os.path.join('font.ttf')

def show_score(surface,text,size,x,y):
    font = pygame.font.Font(font_type,size)# 创建字体
    font_render = font.render(text,True,WHITE)# 渲染文本,抗锯齿
    font_rect = font_render.get_rect()# 获取定位
    font_rect.centerx = x# 设置定位
    font_rect.y = y
    surface.blit(font_render,font_rect)# 显示分数

# 创建生命条
def show_health(surface,hp,x,y):
    if hp < 0:
        hp = 0
    HEALTH_LEHGTH = 100
    HEALTH_HEIGHT = 10
    fill = (hp/100)*HEALTH_LEHGTH # 扣除血量后的长度
    out_rect = pygame.Rect(x,y,HEALTH_LEHGTH,HEALTH_HEIGHT)# 构造外层矩形
    fill_rect = pygame.Rect(x,y,fill,HEALTH_HEIGHT) # 构造内层矩形
    # 显示血条
    pygame.draw.rect(surface,GREEN,fill_rect)
    pygame.draw.rect(surface,WHITE,out_rect,2)

# 添加石头
def add_rocks():
    rock = Rock()
    all_sprite.add(rock)
    rocks.add(rock)

# 创建生命条数
def draw_lives(surf,alives,img,x,y):
    lives_image_rect =  img.get_rect()
    for i in range(alives):
        lives_image_rect.x = x + 30*i
        lives_image_rect.y = y
        surf.blit(img,lives_image_rect)

def Show_init():
    screen.blit(background_image, (0, 0))
    show_score(screen,'太空生存站',60,HEIGHT/4,WIDTH/4)
    show_score(screen,'按任意键开始游戏',30,HEIGHT/2,WIDTH/2)

    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(TIME_UPDATE)
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                pygame.quit()# 按下x后直接关闭窗口
                return True
            elif events.type == pygame.KEYUP:
                waiting = False
                pygame.display.update() # 更新屏幕
                return False
# 创建飞机对象
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_image
        self.image = pygame.transform.scale(player_image,(55,35))

        # 清除黑框
        self.image.set_colorkey(BLACK)
        # self.image = pygame.Surface((30, 30))
        # self.image.fill(RED)
        # 设定初始的位置，或者说获取位置
        self.rect = self.image.get_rect()#pygame.Rect()

        # self.rect.x = 200
        # self.rect.y = 200

        #设置飞船的位置在底部居中
        self.rect.bottom =  HEIGHT-10
        self.rect.centerx = int(WIDTH/2)

        self.speedx = 8 # 设置移动速度
        self.health = 100#设置生命值
        # 创建生命次数
        self.health_alive = 3

        # 设置飞机的圆形半径
        self.radius =  self.rect.width*0.85/2

        # 定义隐藏的值和时间
        self.hidden_bool = False
        self.hidden_time = 0

        # 定义子弹等级
        self.gun_level = 1
        self.gun_time = 0

    def hidden(self):
        self.hidden_bool = True
        self.hidden_time = pygame.time.get_ticks()
        self.rect.bottom = -100
        self.rect.centerx = int(WIDTH / 2)

    def update(self):
            # self.rect.x +=2
            # if self.rect.left>WIDTH:
            #     self.rect.right = 0
            # 获取按键反馈，操控飞机
            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_LEFT]:
                self.rect.x -= self.speedx
            if key_pressed[pygame.K_RIGHT]:
                self.rect.x += self.speedx
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0
            #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

            # 判断死亡后的间隔时间，重新将飞机移回原位置
            if self.hidden_bool and  pygame.time.get_ticks() - self.hidden_time >1000:
                self.hidden_bool = False
                self.rect.bottom = HEIGHT - 10
                self.rect.centerx = int(WIDTH / 2)

            # 吃到道具的时间处理
            now = pygame.time.get_ticks()
            if self.gun_level > 1:
                if now - self.gun_time > 5000:
                    self.gun_level -= 1

    # 创建闪电宝具的效果
    def gun_raise(self):
        self.gun_level += 1
        self.gun_time = pygame.time.get_ticks()

    def shoot(self):
        # 传递飞船的x，top坐标给子弹,死亡间隔时无法发射子弹
        if not(self.hidden_bool):
            if self.gun_level == 1:
                bulletx = self.rect.centerx
                bullety = self.rect.top+5
                bullet = Bullet(bulletx,bullety)
                all_sprite.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun_level >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprite.add(bullet1)
                all_sprite.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
        # 添加到群里面 显示在屏幕上
        # all_sprite.add(bullet)
        # bullets.add(bullet)
        # shoot_sound.play()


class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # 保留原来的图像，实现失帧解决
        self.image_ori = random.choice(rocks_image)
        self.image = self.image_ori
        self.image.set_colorkey(BLACK)

        # 设定初始的位置，或者说获取位置
        self.rect = self.image.get_rect()#pygame.Rect()

        # 设置移动速度， 设置石头的位置随机
        self.speedx = random.randrange(-2,4)
        self.speedy = random.randrange(1,5)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -90)# y的数值设置应该都是负数从上面掉落

        # 设置石头的半径
        self.radius = int(self.rect.width * 0.85/2)

        # 设置旋转的角度和初始角度
        self.tot_degree = 0
        self.rot_degree = random.randrange(-5,5)

    def rotate(self):

        # 实现旋转的动画，解决失帧问题
        self.tot_degree += self.rot_degree
        self.tot_degree %= 360
        self.image = pygame.transform.rotate(self.image_ori,self.tot_degree)

        # 转动重新定位中心点
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        # 当石头掉出窗口外时要重新生成xy坐标
        self.rotate()
        if self.rect.bottom  > HEIGHT+10 or self.rect.left<-20 or self.rect.right>WIDTH+20:
            self.speedx = random.randrange(-2, 10)
            self.speedy = random.randrange(1, 10)
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.rect.x += self.speedx
            self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):# 接受飞船的参数
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_image
        self.image.set_colorkey(BLACK)
        # 设定初始的位置，或者说获取位置
        self.rect = self.image.get_rect()#pygame.Rect()

        self.rect.x =  x
        self.rect.y =  y
        # 设置移动速度
        self.speedy = 10

    def update(self):
        self.rect.y -= self.speedy
        # 判断出去窗口以后删除子弹
        if self.rect.bottom < 0:
            self.kill()

class Power(pygame.sprite.Sprite):
    def __init__(self,center):# 接受飞船的参数
        pygame.sprite.Sprite.__init__(self)
        self.type_list = ['gun','shield']
        self.type = random.choice(self.type_list)
        self.image = power_image[self.type]
        self.image.set_colorkey(BLACK)
        # 设定初始的位置，或者说获取位置
        self.rect = self.image.get_rect()#pygame.Rect()

        self.rect.center = center
        # 设置移动速度
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
            # 判断出去窗口以后删除道具
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,size): # 接受爆炸位置和爆炸种类
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_image[self.size][0]
        self.number = 0 # 用于替换爆炸动画
        self.last_time = pygame.time.get_ticks()# 记录上一次更新图片的时间
        self.change_time = 50 # 以50毫秒为一个周期更换图片
        self.rect = self.image.get_rect()
        self.rect.center = center  # 设置爆炸中心位置


    def update(self):
        self.now_time = pygame.time.get_ticks() # 获取运行的时间
        if self.now_time-self.last_time > self.change_time:# 判断时间差
            self.last_time = self.now_time
            self.number += 1# 更新动画和时间
            if self.number == len(explosion_image[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_image[self.size][self.number]
                self.rect = self.image.get_rect()
                self.rect.center = center


# 创建子弹和石头的群，判断是否有碰撞

show_init = True
# 保持屏幕在关闭前一直存在，获取用户的活动比如鼠标点击移动
while running:
    if show_init:
        close = Show_init()
        if close:
            break
        show_init = False
        all_sprite = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        pows = pygame.sprite.Group()

        player = Player()
        all_sprite.add(player)
        for i in range(8):
            add_rocks()
        # 创建分数和显示分数
        score = 0

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            running = False
        elif events.type == pygame.KEYDOWN:   
            if events.key == pygame.K_SPACE:
                player.shoot()

    #删除碰撞的石头和子弹
    hits = pygame.sprite.groupcollide(bullets,rocks,True,True)

    for x in hits:
        # 返回的字典中key是子弹，value是石头，分数加上石头的半径
        for rock in hits[x]:
        # 无法直接调hitsdict1[x]，类别是pygame.sprite.Group
        # 值是 rocks 组里和该子弹发生碰撞的石头列表
            score += rock.radius
            expl = Explosion(rock.rect.center, 'lg')
            all_sprite.add(expl)
            if random.random() >0.01:# 调节掉落概率
                pow = Power(rock.rect.center)
                all_sprite.add(pow)
                pows.add(pow)
        # 添加爆炸音效
        random.choice(expl_sound).play()


        # 删除的石头要重新添加回群组,rocks里面
        add_rocks()

     # 飞船和石头碰撞后
    # 返回 一个列表，通过判断列表是否有值来判断是否发生碰撞
    hit_list = pygame.sprite.spritecollide(player,rocks,True,pygame.sprite.collide_circle)
    for hit in hit_list:
        expl2 = Explosion(hit.rect.center, 'sm')
        all_sprite.add(expl2)
        add_rocks()
        player.health -= hit.radius*5
        if player.health <= 0:
            expl3 = Explosion(player.rect.center, 'player')
            all_sprite.add(expl3)
            player_expl_sound.play()
            player.hidden()# 死亡时要隐藏一段时间
            player.health_alive -= 1
            player.health =  100
        if player.health_alive == 0:
                show_init = True


    # 吃到道具后的效果判断
    pow_hit_list = pygame.sprite.spritecollide(player, pows, True)
    for hit in pow_hit_list:
        if hit.type == 'shield':
            player.health += 10
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == 'gun':
            player.gun_raise()
            gun_sound.play()
    # 增加游戏背景
    screen.blit(background_image,(0,0))
    # 实时更新屏幕
    # screen.fill(BLACK)

    clock.tick(TIME_UPDATE)

    # 将所有的sprite显示在屏幕上screen应该是sprite要显示的位置
    all_sprite.draw(screen)#all_sprite.draw(),

    # 显示分数
    show_score(screen,str(score),18,WIDTH/2,10)

    # 显示血条
    show_health(screen,player.health,10,8)

    # 显示生命条数
    draw_lives(screen,player.health_alive,player_mini_image,WIDTH-100,8)
    # 播放背景音乐
    pygame.mixer.music.set_volume(0.3) #设置音量大小
    pygame.mixer.music.play(-1)# -1是无限循环播放？

    #两个update，一个更新sprite的位置，一个更新屏幕
    all_sprite.update()
    pygame.display.update()

pygame.quit()