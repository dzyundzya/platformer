import pygame
import sys
import os
import pygame.freetype


"""Перменные
"""

# Размер окна.
worldx = 960
worldy = 720

# Частота кадров.
fps = 40
# Цикл анимации.
ani = 4
# фон игрового мира
world = pygame.display.set_mode([worldx, worldy])

# Цвет хитбокса.
ALPHA = (156, 156, 156)

# Цвет шрифта.
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
GREEN_YELLOW = (173, 255, 47)

forwardx = 600
backwardx = 230


"""Объекты
"""


# Отоброжение текста.
def stats(score, health):
    myfont.render_to(world, (4, 4), 'Score:' + str(score), GOLD, None, size=36)
    myfont.render_to(world, (4, 72), 'Health:' + str(health), GREEN_YELLOW, None, size=40)


# x location, y location, img width, img height, img file
class Platform(pygame.sprite.Sprite):
    """
    Создание платформ.
    """

    def __init__(self, xloc, yloc, imgw, imgh, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('images', img)).convert()
        self.image.convert_alpha()
        self.image.set_colorkey(ALPHA)
        self.rect = self.image.get_rect()
        self.rect.y = yloc
        self.rect.x = xloc


class Player(pygame.sprite.Sprite):
    """
    Создание игрового персонажа.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.movex = 0  # Перемещение по Х.
        self.movey = 0  # Перемещение по Y.
        self.frame = 0  # Подсчет кадров.
        self.health = 10
        self.score = 0
        self.damage = 0
        # Код прыжка.
        self.is_jumping = True
        self.is_falling = False

        for i in range(1, 5):
            img = pygame.image.load(os.path.join('images',
                                    'hero' + str(i) + '.png')).convert()
            img.convert_alpha()  # оптимизация альфа-диапазона
            # Все пиксили совподающие с этой командой, станут прозрачными.
            img.set_colorkey(ALPHA)

            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()

    def gravity(self):
        if self.is_jumping:
            self.movey += 3.2  # С каким ускорением персонаж будет падать

    def control(self, x, y):
        """
        Управление перемещением главного персонажа.
        """

        self.movex += x

    def jump(self):
        if self.is_jumping is False:
            self.is_falling = False
            self.is_jumping = True

    def update(self):
        """
        Обновление позиции спрайта
        """

        # Движение влево.
        if self.movex < 0:
            self.is_jumping = True  # Включает гравитацию.
            self.frame += 1
            if self.frame > 3 * ani:
                self.frame = 0
            self.image = pygame.transform.flip(self.images[self.frame//ani],
                                               True, False)

        # Движение вправо.
        if self.movex > 0:
            self.is_jumping = True
            self.frame += 1
            if self.frame > 3 * ani:
                self.frame = 0
            self.image = self.images[self.frame//ani]

        # Урон от врага.
        enemy_hit_list = pygame.sprite.spritecollide(self, enemy_list, False)
        if self.damage == 0:
            for enemy in enemy_hit_list:
                if not self.rect.contains(enemy):
                    self.damage = self.rect.colliderect(enemy)
        
        if self.damage == 1:
            idx = self.rect.collidelist(enemy_hit_list)
            if idx == -1:
                self.damage = 0
                self.health -= 1


        # Столкновение с землей.
        ground_hit_list = pygame.sprite.spritecollide(self, ground_list, False)
        for g in ground_hit_list:
            self.movey = 0
            self.rect.bottom = g.rect.top
            self.is_jumping = False  # Прикратить прыжок.

        # Падение за пределы игровой сцены.
        if self.rect.y > worldy:
            self.health -= 1
            print(self.health)
            self.rect.x = tx
            self.rect.y = ty

        # Касание монеты.
        loot_hit_list = pygame.sprite.spritecollide(self, loot_list, False)
        for loot in loot_hit_list:
            loot_list.remove(loot)
            self.score += 1
            print(self.score)

        plat_hit_list = pygame.sprite.spritecollide(self, plat_list, False)
        for p in plat_hit_list:
            self.is_jumping = False  # Прикратить прыжок
            self.movey = 0
            # Анализ события соприкосновения с поверхностью земли(платформы)
            if self.rect.bottom <= p.rect.bottom:
                self.rect.bottom = p.rect.top
            else:
                self.movey += 3.2
        
        health_hit_list = pygame.sprite.spritecollide(self, health_list, False)
        for health in health_hit_list:
            health_list.remove(health)
            self.health += 5

        # Взлет при начале прыжка.
        if self.is_jumping and self.is_falling is False:
            self.is_falling = True
            self.movey -= 33  # На какую высоту прыгать.

        self.rect.x += self.movex
        self.rect.y += self.movey


class Enemy(pygame.sprite.Sprite):
    """
    Создание врага - летучая мышь.
    """

    def __init__(self, x, y, eny):
        pygame.sprite.Sprite.__init__(self)

        self.images = []
        for i in range(1, 6):
            img = pygame.image.load(os.path.join('images',
                                    eny + str(i) + '.png')).convert()
            img.convert_alpha()  # оптимизация альфа-диапазона
            # Все пиксили совподающие с этой командой, станут прозрачными.
            img.set_colorkey(ALPHA)

            self.images.append(img)
            self.image = self.images[0]
            self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.counter = 0

    def move(self):
        """
        Перемещение врага.
        """

        distance = 30
        speed = 5

        if self.counter >= 0 and self.counter <= distance:
            self.rect.x += speed
        elif self.counter >= distance and self.counter <= distance * 2:
            self.rect.x -= speed
        else:
            self.counter = 0

        self.counter += 1


class Level:

    def ground(lvl, gloc, tx, ty):
        ground_list = pygame.sprite.Group()
        i = 0
        if lvl == 1:
            while i < len(gloc):
                ground = Platform(gloc[i], worldy - ty, tx, ty, 'tile.png')
                ground_list.add(ground)
                i = i + 1

        if lvl == 2:
            print('Level' + str(lvl))

        return ground_list

    def bad(lvl, eloc):
        if lvl == 1:
            enemy = Enemy(eloc[0], eloc[1], 'enemy')  # Создаем врага.
            enemy_list = pygame.sprite.Group()  # Создаем массив врагов.
            enemy_list.add(enemy)  # Добавляем врага в созданный массив.
        if lvl == 2:
            print('Level' + str(lvl))
        return enemy_list

    def platform(lvl, tx, ty):
        plat_list = pygame.sprite.Group()
        ploc = []
        i = 0
        if lvl == 1:
            ploc.append((200, worldy - ty - 194, 2))  # Нижняя 1
            ploc.append((300, worldy - ty - 384, 3))  # Верхняя
            ploc.append((600, worldy - ty - 194, 3))  # Нижняя 2
            ploc.append((1500, worldy - ty - 194, 3))
            while i < len(ploc):
                j = 0
                while j <= ploc[i][2]:
                    plat = Platform((ploc[i][0] + (j * tx)),
                                    ploc[i][1], tx, ty, 'tile.png')
                    plat_list.add(plat)
                    j = j + 1
                print('run' + str(i) + str(ploc[i]))
                i = i + 1

        if lvl == 2:
            print('Level' + str(lvl))

        return plat_list

    def loot(lvl):
        if lvl == 1:
            loot_list = pygame.sprite.Group()
            loot = Platform(450, 200, tx, ty, 'coin.png')
            loot_list.add(loot)
            loot = Platform(500, 200, tx, ty, 'coin.png')
            loot_list.add(loot)
            loot = Platform(650, 400, tx, ty, 'coin.png')
            loot_list.add(loot)
        if lvl == 2:
            print(lvl)
        return loot_list

    def health(lvl):
        if lvl == 1:
            health_list = pygame.sprite.Group()
            health5 = Platform(1600, 400, tx, ty, 'health5.png')
            health_list.add(health5)
        if lvl == 2:
            print(lvl)
        return health_list


"""Настройка
"""

backdrop = pygame.image.load(os.path.join('images', 'stage.png'))
# внутренние часы
clock = pygame.time.Clock()
pygame.init()

backdropbox = world.get_rect()

# Главный цикл.
main = True

# Создать персонажа.
player = Player()
# Задать координаты x,y.
player.rect.x = 0
player.rect.y = 600
player_list = pygame.sprite.Group()
player_list.add(player)
steps = 10  # Количество пикселей для перемещения.

# Создание врага-летучая мышь.
eloc = []
eloc = [625, 400]
enemy_list = Level.bad(1, eloc)

# Логика формирующая "Землю"
gloc = []
tx = 64
ty = 64

i = 0
while i <= (worldx / tx) + tx:
    gloc.append(i * tx)
    i = i + 1

# Выхов набора земли
ground_list = Level.ground(1, gloc, tx, ty)
# Вызов набора платформ
plat_list = Level.platform(1, tx, ty)
# Вызов монетки
loot_list = Level.loot(1)

health_list = Level.health(1)


# Использование шрифта.
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'spydi.ttf')
font_size = tx
pygame.freetype.init()
myfont = pygame.freetype.Font(font_path, font_size)

"""Главный цикл
"""

while main:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                main = False

        if event.type == pygame.KEYDOWN:
            if event.key == ord('q'):
                pygame.quit
                try:
                    sys.exit()
                finally:
                    main = False
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(-steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(steps, 0)
            if event.key == pygame.K_UP or event.key == ord('w'):
                player.jump()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                player.control(steps, 0)
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                player.control(-steps, 0)

    # Прокрутка игровой сцены в прямом направлении.
    if player.rect.x >= forwardx:
        scroll = player.rect.x - forwardx
        player.rect.x = forwardx
        for p in plat_list:
            p.rect.x -= scroll  # Прокрутка персонажа.
        for e in enemy_list:
            e.rect.x -= scroll  # Прокрутка врага.
        for l in loot_list:
            l.rect.x -= scroll  # Прокрутка предмета
        for h in health_list:
            h.rect.x -= scroll

    # Прокрутка игровой сцены в обратном направлении.
    if player.rect.x <= backwardx:
        scroll = backwardx - player.rect.x
        player.rect.x = backwardx
        for p in plat_list:
            p.rect.x += scroll
        for e in enemy_list:
            e.rect.x += scroll
        for l in loot_list:
            l.rect.x += scroll
        for h in health_list:
            h.rect.x += scroll

    world.blit(backdrop, backdropbox)
    player.update()  # Обновляет положение персонажа.
    player.gravity()  # Проверка гравитации.
    player_list.draw(world)  # Нарисовать игрока.
    enemy_list.draw(world)  # Обновить врагов.
    ground_list.draw(world)  # Обновить землю.
    plat_list.draw(world)  # Обновить платформы.
    loot_list.draw(world)  # Обновляетя монетку.
    for e in enemy_list:
        e.move()
    health_list.draw(world)
    stats(player.score, player.health)
    pygame.display.flip()
    clock.tick(fps)


