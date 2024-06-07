import sdl2
import sdl2.ext
import ctypes
from sdl2.sdlttf import *


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

    def is_outside(self):
        if self.prop:
            if self.pos_x >= 620 or self.pos_x <= 0:
                self.velocity_x = -self.velocity_x
            if self.pos_y >= 900 or self.pos_y <= 0:
                self.velocity_y = -self.velocity_y

    def set_pos_x(self, pos_x):
        self.pos_x = pos_x

    def get_pos_x(self):
        return self.pos_x

    def set_pos_y(self, pos_y):
        self.pos_y = pos_y

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


class Game:
    def __init__(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
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

    def shoot(self):
        self.p_bullets.append([self.playerX + 29, self.playerY])

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

    def run(self):
        meteor1 = Position(450, 100, 5, 5, True, 72)
        meteor2 = Position(200, 500, 5, 5, True, 72)
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
                        self.accelerationX = -0.5
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.accelerationX = 0.5
                    elif event.key.keysym.sym == sdl2.SDLK_UP:
                        self.accelerationY = -0.5
                    elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.accelerationY = 0.5
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        self.running = False
                        break
                    elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                        self.shoot()
                    elif event.key.keysym.sym == sdl2.SDLK_r:
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
            if meteor2.is_colision_with_meteor(player_x=self.playerX, player_y=self.playerY, prop_width=58,
                                               prop_height=37):
                self.velocityY = -self.velocityY
                self.velocityX = -self.velocityX
                meteor2.change_direction_and_speed()
            for bullet in self.p_bullets:
                bullet[0] += 10
            self.p_bullets = [bullet for bullet in self.p_bullets if bullet[1] > 0]
            sdl2.SDL_RenderClear(self.ren)
            self.renderTexture(self.background, self.ren, 0, 0)
            self.renderTexture(self.ship, self.ren, int(self.playerX), int(self.playerY))
            self.renderTexture(self.meteor, self.ren, meteor1.get_pos_x(), meteor1.get_pos_y())
            self.renderTexture(self.meteor, self.ren, meteor2.get_pos_x(), meteor2.get_pos_y())
            sdl2.SDL_SetRenderDrawColor(self.ren, 255, 0, 0, 255)
            sdl2.SDL_SetRenderDrawColor(self.ren, 255, 0, 0, 255)
            for bullet in self.p_bullets:
                sdl2.SDL_RenderDrawLine(self.ren, int(bullet[0]), int(bullet[1]), int(bullet[0]) + 15, int(bullet[1]))

            sdl2.SDL_RenderPresent(self.ren)
        sdl2.SDL_DestroyTexture(self.background)
        sdl2.SDL_DestroyTexture(self.ship)
        sdl2.SDL_DestroyRenderer(self.ren)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_QUIT()
        return 0

    def update(self):
        return 0;

    def render(self):
        self.window.refresh()


if __name__ == '__main__':
    game = Game()
    game.run()
