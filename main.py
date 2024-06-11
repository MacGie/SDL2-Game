import random
import sdl2
import ctypes
import sdl2.ext
from sdl2.sdlttf import *
from prop_managment import Position


class Game:
    def __init__(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"Cannot initialize SDL2: {sdl2.SDL_GetError().decode('utf-8')}")
        if TTF_Init() == -1:
            raise RuntimeError(f"Cannot initialize SDL_ttf: {TTF_GetError().decode('utf-8')}")
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
        self.shoot_down = 0
        self.hard_mode = False

    def renderText(self, message, fontFile, color, fontSize, renderer, x, y):
        font = TTF_OpenFont(fontFile.encode('utf-8'), fontSize)
        if not font:
            print(f"Failed to load font: {TTF_GetError().decode('utf-8')}")
            return
        sdl_color = sdl2.SDL_Color(color[0], color[1], color[2])
        text_surface = TTF_RenderText_Solid(font, message.encode('utf-8'), sdl_color)
        if not text_surface:
            TTF_CloseFont(font)
            print(f"Nie udało się wczytać czcionki: {TTF_GetError().decode('utf-8')}")
            return
        text_texture = sdl2.SDL_CreateTextureFromSurface(renderer, text_surface)
        if not text_texture:
            sdl2.SDL_FreeSurface(text_surface)
            TTF_CloseFont(font)
            print(f"Nie udało się stworzyć textury: {sdl2.SDL_GetError().decode('utf-8')}")
            return
        text_rect = sdl2.SDL_Rect(x, y, text_surface.contents.w, text_surface.contents.h)
        sdl2.SDL_RenderCopy(renderer, text_texture, None, text_rect)
        sdl2.SDL_FreeSurface(text_surface)
        sdl2.SDL_DestroyTexture(text_texture)
        TTF_CloseFont(font)

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
                        self.accelerationX = -0.3
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT:
                        self.accelerationX = 0.3
                    elif event.key.keysym.sym == sdl2.SDLK_UP:
                        self.accelerationY = -0.3
                    elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                        self.accelerationY = 0.3
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        self.running = False
                        break
                    elif event.key.keysym.sym == sdl2.SDLK_SPACE:
                        self.shoot()
                    elif event.key.keysym.sym == sdl2.SDLK_r:
                        self.hp = 100
                        self.playerY = 0
                        self.playerX = 0
                        self.shoot_down = 0
                        self.p_bullets = []
                        self.run()
                    elif event.key.keysym.sym == sdl2.SDLK_t:
                        self.hp = 100
                        self.playerY = 0
                        self.playerX = 0
                        self.p_bullets=[]
                        self.shoot_down=0
                        if not self.hard_mode:
                            self.hard_mode = True
                        else:
                            self.hard_mode = False
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
                sdl2.SDL_Delay(5)
                meteor2.velocity_x, meteor2.velocity_y = meteor1.collision(meteor2.velocity_x,
                                                                           meteor2.velocity_y,
                                                                           meteor2.get_pos_x(),
                                                                           meteor2.get_pos_y(), 3, self.hard_mode)
            if meteor1.is_colision_with_meteor(player_x=self.playerX, player_y=self.playerY, prop_width=58,
                                               prop_height=37):
                self.velocityX, self.velocityY = meteor1.collision(self.velocityX, self.velocityY,
                                                                   self.playerX, self.playerY, 0.2, self.hard_mode)
                self.hp = self.hp - 10
            if meteor2.is_colision_with_meteor(player_x=self.playerX, player_y=self.playerY, prop_width=58,
                                               prop_height=37):
                self.velocityY = -self.velocityY
                self.velocityX = -self.velocityX
                meteor2.collision(self.velocityX, self.velocityY, self.playerX, self.playerY, 0.5,
                                  hard_mode=self.hard_mode)
                self.hp = self.hp - 10

            for bullet in self.p_bullets:
                bullet[0] += 10
            self.p_bullets = [bullet for bullet in self.p_bullets if bullet[0] < 800]

            if self.bang_bang(alien1, 150, 102, self.p_bullets):
                alien1.set_pos_x(random.randint(700, 900))
                alien1.time = 0
                self.shoot_down += 1
                while alien1.get_pos_y() >= alien2.get_pos_y() + 150:
                    alien1.set_pos_y(random.randint(0, 450))
            if self.bang_bang(alien2, 150, 102, self.p_bullets):
                alien2.set_pos_x(random.randint(700, 900))
                print("BANG")
                alien2.time = 0
                self.shoot_down += 1
                while alien2.get_pos_y() >= alien1.get_pos_y() + 150:
                    alien2.set_pos_y(random.randint(0, 450))
            if alien1.is_ctf:
                self.hp = self.hp - 10
                alien1.is_ctf = False
            if alien2.is_ctf:
                self.hp = self.hp - 10
                alien2.is_ctf = False
            # Renderowanei textur
            sdl2.SDL_RenderClear(self.ren)
            self.renderTexture(self.background, self.ren, 0, 0)
            self.renderTexture(self.ship, self.ren, int(self.playerX), int(self.playerY))
            self.renderTexture(self.meteor, self.ren, meteor1.get_pos_x(), meteor1.get_pos_y())
            self.renderTexture(self.meteor, self.ren, meteor2.get_pos_x(), meteor2.get_pos_y())
            self.renderTexture(self.aliens, self.ren, alien1.get_pos_x(), alien1.get_pos_y())
            self.renderTexture(self.aliens, self.ren, alien2.get_pos_x(), alien2.get_pos_y())
            self.renderTexture(self.stats, self.ren, 0, 600)
            self.renderText(f"HP: {self.hp}", 'font/PixelGameFont.ttf', [255, 255, 255], 30, self.ren, 50, 700)
            self.renderText(f"Zestrzelone statki : {self.shoot_down}", 'font/PixelGameFont.ttf', [255, 255, 255], 25,
                            self.ren, 250, 700)
            if not self.hard_mode:
                self.renderText(f"Hard Mode : OFF", 'font/PixelGameFont.ttf', [255, 255, 255], 20, self.ren, 250, 750)
            else:
                self.renderText(f"Hard Mode : ON", 'font/PixelGameFont.ttf', [255, 255, 255], 20, self.ren, 250, 750)
            ''' Przy porażce restart gry'''
            self.renderText(f"R - Restart", 'font/PixelGameFont.ttf', [255, 255, 255], 15, self.ren, 650, 620)
            self.renderText(f"T - Hard Mode", 'font/PixelGameFont.ttf', [255, 255, 255], 15, self.ren, 650, 640)

            if self.hp <= 0:
                self.hp = 100
                self.shoot_down = 0
                self.run()requirements

            sdl2.SDL_SetRenderDrawColor(self.ren, 255, 0, 0, 255)
            for bullet in self.p_bullets:
                sdl2.SDL_RenderDrawLine(self.ren, int(bullet[0]), int(bullet[1]), int(bullet[0]) + 15, int(bullet[1]))

            sdl2.SDL_RenderPresent(self.ren)

        # Sprzatanie
        sdl2.SDL_DestroyTexture(self.background)
        sdl2.SDL_DestroyTexture(self.ship)
        sdl2.SDL_DestroyRenderer(self.ren)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_QUIT()
        return 0

    def render(self):
        self.window.refresh()


if __name__ == '__main__':
    game = Game()
    game.run()
