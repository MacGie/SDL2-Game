import sdl2
import sdl2.ext
import ctypes
from sdl2.sdlttf import *


class Position:
    def __init__(self, start_x, start_y, velocity, prop, r):
        self.start_x = start_x
        self.start_y = start_y
        self.velocity = velocity
        self.pos_y = start_y
        self.pos_x = start_x
        self.prop = prop
        self.r = r
        self.rx = self.pos_x + r
        self.ry = self.pos_y + r

    def is_outside(self):
        if self.prop:
            if self.pos_x >= 620:
                self.pos_x = self.start_x
            if self.pos_y >= 900:
                self.pos_y = self.start_y

    def set_pos_x(self, pos_x):
        self.pos_x = pos_x

    def get_pos_x(self):
        return self.pos_x

    def set_pos_y(self, pos_y):
        self.pos_y = pos_y

    def move_on(self, vertical):
        if vertical:
            self.set_pos_y(pos_y=self.pos_y + self.velocity)
            self.ry = self.pos_y + self.r
        else:
            self.set_pos_x(pos_x=self.pos_x + self.velocity)
            self.rx = self.pos_x + self.r

    def get_pos_y(self):
        return self.pos_y

    def is_colision(self, player_x, player_y):
        distance_x_0 = player_x - self.rx
        distance_y_0 = player_y - self.ry
        distance_x_m = (player_x+58) - self.rx
        distance_y_m = (player_y+37) - self.ry
        distance_0_0 = (distance_x_0 ** 2 + distance_y_0 ** 2) ** 0.5
        distance_x_y = (distance_x_m ** 2 + distance_y_m ** 2) ** 0.5
        distance_0_y = (distance_x_0 ** 2 + distance_y_m ** 2) ** 0.5
        distance_x_0 = (distance_x_m ** 2 + distance_y_0 ** 2) ** 0.5
        return distance_0_0 <= self.r or distance_x_y <= self.r or distance_x_0 <= self.r or distance_0_y <= self.r
class Game:
    def __init__(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"Cannot initialize SDL2: {sdl2.SDL_GetError().decode('utf-8')}")
        self.window = sdl2.SDL_CreateWindow(
            b'GAME',
            100,
            100,
            800,
            600,
            sdl2.SDL_WINDOW_SHOWN
        )
        self.running = True
        self.ren = sdl2.SDL_CreateRenderer(
            self.window,
            -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        img_path = 'img'
        self.background = self.loadTexture('img/background.bmp', renderer=self.ren)
        self.ship = self.loadTexture('img/ship.bmp', renderer=self.ren)
        self.meteor = self.loadTexture('img/asteroida.bmp', renderer=self.ren)
        self.playerX = 0
        self.playerY = 0
        self.velocity = 0
        self.lost = False

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
        meteor1 = Position(450, -100, 5, True, 72)
        meteor2 = Position(200, -100, 5, True, 72)
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
                        self.playerX -= 10
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.playerX += 10
                    elif event.key.keysym.sym == sdl2.SDLK_UP:
                        self.playerY -= 10
                    elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.playerY += 10
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        self.running = False
                        break

            meteor1.is_outside()
            meteor1.move_on(True)
            meteor2.is_outside()
            meteor2.move_on(True)
            if meteor2.is_colision(player_x=self.playerX,player_y=self.playerY) or meteor1.is_colision(player_x=self.playerX,player_y=self.playerY):
                print("KOLIZJA !!!")

            sdl2.SDL_RenderClear(self.ren)
            self.renderTexture(self.background, self.ren, 0, 0)
            self.renderTexture(self.ship, self.ren, self.playerX, self.playerY)
            self.renderTexture(self.meteor, self.ren, meteor1.get_pos_x(), meteor1.get_pos_y())
            self.renderTexture(self.meteor, self.ren, meteor2.get_pos_x(), meteor2.get_pos_y())
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
