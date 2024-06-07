import random
import sdl2
import sdl2.ext
import ctypes
from sdl2.sdlttf import *
import math
import time


class Position:
    def __init__(self, start_x, start_y, velocity_x, velocity_y, prop, r):
        self.start_x = start_x
        self.start_y = start_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.pos_y = start_y
        self.pos_x = start_x
        self.prop = prop
        self.r = r
        self.rx = self.pos_x + r
        self.ry = self.pos_y + r
        self.amplitude = 120
        self.frequency = 0.1
        self.time = 0
        self.shoot_cooldown = 0
        self.shoot_frequency = 80
        self.is_ctf = False

    def is_outside(self):
        if self.pos_x >= 850 or self.pos_x <= -200:
            self.velocity_x = -self.velocity_x
        if self.pos_y >= 850 or self.pos_y <= -200:
            self.velocity_y = -self.velocity_y

    def set_pos_x(self, pos_x):
        self.pos_x = pos_x

    def get_pos_x(self):
        return self.pos_x

    def set_pos_y(self, pos_y):
        self.pos_y = pos_y

    def alien_move_on(self):
        self.time += 1
        new_x = self.start_x - self.velocity_x * self.time
        y = self.amplitude * math.sin(self.frequency * self.time)
        new_y = self.start_y + y
        if new_x < -500:
            self.set_pos_x(self.start_x)
            self.time = 0
            self.is_ctf = True
        self.set_pos_x(int(new_x))
        self.set_pos_y(int(new_y))
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_frequency

    def move_on(self):
        self.set_pos_y(pos_y=self.pos_y + self.velocity_y)
        self.set_pos_x(pos_x=self.pos_x + self.velocity_x)
        self.ry = self.pos_y + self.r
        self.rx = self.pos_x + self.r

    def get_pos_y(self):
        return self.pos_y

    def is_colision_with_meteor(self, player_x, player_y, prop_width, prop_height):
        distance_x_0 = player_x - self.rx
        distance_y_0 = player_y - self.ry
        distance_x_m = (player_x + prop_width) - self.rx
        distance_y_m = (player_y + prop_height) - self.ry
        distance_0_0 = (distance_x_0 ** 2 + distance_y_0 ** 2) ** 0.5
        distance_x_y = (distance_x_m ** 2 + distance_y_m ** 2) ** 0.5
        distance_0_y = (distance_x_0 ** 2 + distance_y_m ** 2) ** 0.5
        distance_x_0 = (distance_x_m ** 2 + distance_y_0 ** 2) ** 0.5
        return distance_0_0 <= self.r or distance_x_y <= self.r or distance_x_0 <= self.r or distance_0_y <= self.r

    def change_direction_and_speed(self):
        self.velocity_x = -self.velocity_x
        self.velocity_y = -self.velocity_y

    def shoot(self):
        bullet_x = self.get_pos_x() - 0
        bullet_y = self.get_pos_y() + 20
        return bullet_x, bullet_y


class Game:
    def __init__(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0: \
                raise RuntimeError(f"Cannot initialize SDL2: {sdl2.SDL_GetError().decode('utf-8')}")
        self.window = sdl2.SDL_CreateWindow(
            b'GAME',
            100,
            100,
            800,
            800,
            sdl2.SDL_WINDOW_SHOWN
        )
        self.running = True
        self.ren = sdl2.SDL_CreateRenderer(
            self.window,
            -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        self.background = self.loadTexture('img/background.bmp', renderer=self.ren)
        self.ship = self.loadTexture('img/ship.bmp', renderer=self.ren)
        self.meteor = self.loadTexture('img/asteroida.bmp', renderer=self.ren)
        self.playerX = 0
        self.playerY = 0
        self.velocityY = 0
        self.velocityX = 0
        self.accelerationX = 0
        self.accelerationY = 0
        self.lost = False
        self.shield = True
        self.p_bullets = []
        self.aliens = self.loadTexture('img/gflota.bmp', renderer=self.ren)
        self.hp = 100
        self.stats = self.loadTexture('img/tab.bmp', renderer=self.ren)
        self.aliens_bullet = []

    def shoot(self):
        self.p_bullets.append([self.playerX + 40, self.playerY + 15])

    def loadTexture(self, filePath, renderer):
        img = sdl2.SDL_LoadBMP(str.encode(filePath))
        if img:
            texture = sdl2.SDL_CreateTextureFromSurface(renderer, img)
            sdl2.SDL_FreeSurface(img)
            if not texture:
                print('Błąd wczytania textury')
        else:
            print('Błąd wczytania pliku z tekstura')

        return texture

    def renderTexture(self, texture, render, x, y):
        loc = sdl2.SDL_Rect(x, y, 0, 0)
        w = ctypes.pointer(ctypes.c_long(0))
        h = ctypes.pointer(ctypes.c_long(0))
        sdl2.SDL_QueryTexture(texture, None, None, w, h)
        loc.w = w.contents.value
        loc.h = h.contents.value
        sdl2.SDL_RenderCopy(render, texture, None, loc)

    def bang_bang(self, prop, width, height, bullets):
        for bullet in bullets:
            bullet_x, bullet_y = bullet
            if (prop.get_pos_x() <= bullet_x <= prop.get_pos_x() + width) and (
                    prop.get_pos_y() <= bullet_y <= prop.get_pos_y() + height):
                self.p_bullets.remove(bullet)
                return True
        return False

    def run(self):
        meteor1 = Position(450, 100, 5, 5, False, 72)
        meteor2 = Position(200, 500, 5, 5, False, 72)
        alien1 = Position(800, 200, 4, 0, True, 60)
        alien2 = Position(800, 400, 4, 0, True, 60)
        if not self.background:
            sdl2.SDL_DestroyTexture(self.background)
            sdl2.SDL_DestroyRenderer(self.ren)
            sdl2.SDL_DestroyWindow(self.window)
            sdl2.SDL_QUIT()
        while self.running:
            events = sdl2.ext.get_events()

            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
                    break
                if event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT:
                        self.accelerationX = -0.4
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.accelerationX = 0.4
                    elif event.key.keysym.sym == sdl2.SDLK_UP:
                        self.accelerationY = -0.4
                    elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.accelerationY = 0.4
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        self.running = False
                        break
                    elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                        self.shoot()
                    elif event.key.keysym.sym == sdl2.SDLK_r:
                        self.hp = 100
                        self.run()

                if event.type == sdl2.SDL_KEYUP:
                    if event.key.keysym.sym in [sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT]:
                        self.accelerationX = 0
                    if event.key.keysym.sym in [sdl2.SDLK_UP, sdl2.SDLK_DOWN]:
                        self.accelerationY = 0

            self.velocityX += self.accelerationX
            self.velocityY += self.accelerationY
            self.playerX += self.velocityX
            self.playerY += self.velocityY

            if self.playerX < 0:
                self.playerX = 0
                self.velocityX = 0
            if self.playerX + 58 > 800:
                self.playerX = 800 - 58
                self.velocityX = 0
            if self.playerY < 0:
                self.playerY = 0
                self.velocityY = 0
            if self.playerY + 37 > 600:
                self.playerY = 600 - 37
                self.velocityY = 0

            sdl2.SDL_Delay(10)
            meteor1.is_outside()
            meteor1.move_on()
            meteor2.is_outside()
            meteor2.move_on()
            alien1.alien_move_on()
            alien2.alien_move_on()

            if meteor1.is_colision_with_meteor(
                    player_y=meteor2.get_pos_y(), player_x=meteor2.get_pos_x(), prop_width=144, prop_height=130):
                sdl2.SDL_Delay(15)
                meteor1.change_direction_and_speed()
            if meteor2.is_colision_with_meteor(player_x=meteor1.get_pos_x(), player_y=meteor1.get_pos_y(),
                                               prop_width=144, prop_height=130):
                sdl2.SDL_Delay(15)
                meteor2.change_direction_and_speed()

            if meteor1.is_colision_with_meteor(player_x=self.playerX, player_y=self.playerY, prop_width=58,
                                               prop_height=37):
                self.velocityX = -self.velocityX
                self.velocityY = -self.velocityY
                meteor1.change_direction_and_speed()
                self.hp = self.hp - 10
            if meteor2.is_colision_with_meteor(player_x=self.playerX, player_y=self.playerY, prop_width=58,
                                               prop_height=37):
                self.velocityY = -self.velocityY
                self.velocityX = -self.velocityX
                meteor2.change_direction_and_speed()
                self.hp = self.hp - 10

            # Update bullets
            for bullet in self.p_bullets:
                bullet[0] += 10
            self.p_bullets = [bullet for bullet in self.p_bullets if bullet[0] < 800]

            # Check for collisions with aliens
            if self.bang_bang(alien1, 150, 102, self.p_bullets):
                alien1.set_pos_x(random.randint(700, 900))
                print("BANG")
                alien1.time = 0
                while alien1.get_pos_y() >= alien2.get_pos_y() + 150:
                    alien1.set_pos_y(random.randint(0, 450))
            if self.bang_bang(alien2, 150, 102, self.p_bullets):
                alien2.set_pos_x(random.randint(700, 900))
                print("BANG")
                alien2.time = 0
                while alien2.get_pos_y() >= alien1.get_pos_y() + 150:
                    alien2.set_pos_y(random.randint(0, 450))
            if alien1.is_ctf:
                self.hp = self.hp - 10
                alien1.is_ctf = False
            if alien2.is_ctf:
                self.hp = self.hp - 10
                alien2.is_ctf = False
            # Render everything
            sdl2.SDL_RenderClear(self.ren)
            self.renderTexture(self.background, self.ren, 0, 0)
            self.renderTexture(self.ship, self.ren, int(self.playerX), int(self.playerY))
            self.renderTexture(self.meteor, self.ren, meteor1.get_pos_x(), meteor1.get_pos_y())
            self.renderTexture(self.meteor, self.ren, meteor2.get_pos_x(), meteor2.get_pos_y())
            self.renderTexture(self.aliens, self.ren, alien1.get_pos_x(), alien1.get_pos_y())
            self.renderTexture(self.aliens, self.ren, alien2.get_pos_x(), alien2.get_pos_y())
            self.renderTexture(self.stats, self.ren, 0, 600)
            print(self.hp)
            if self.hp <= 0:
                self.hp = 100
                self.run()
            sdl2.SDL_SetRenderDrawColor(self.ren, 255, 0, 0, 255)
            for bullet in self.p_bullets:
                sdl2.SDL_RenderDrawLine(self.ren, int(bullet[0]), int(bullet[1]), int(bullet[0]) + 15, int(bullet[1]))

            for bullet in self.aliens_bullet:
                sdl2.SDL_RenderDrawLine(self.ren, int(bullet[0]), int(bullet[1]), int(bullet[0]) + 15, int(bullet[1]))
            sdl2.SDL_RenderPresent(self.ren)

        # Cleanup
        sdl2.SDL_DestroyTexture(self.background)
        sdl2.SDL_DestroyTexture(self.ship)
        sdl2.SDL_DestroyRenderer(self.ren)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_QUIT()
        return 0

    def update(self):
        return 0

    def render(self):
        self.window.refresh()


if __name__ == '__main__':
    game = Game()
    game.run()
