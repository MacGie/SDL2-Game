import sdl2
import sdl2.ext
import ctypes


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
            sdl2.SDL_RenderClear(self.ren)
            bW = ctypes.pointer(ctypes.c_long(0))
            bH = ctypes.pointer(ctypes.c_long(0))
            self.renderTexture(self.background, self.ren, 0, 0)
            self.renderTexture(self.ship,self.ren,100,100)
            sdl2.SDL_RenderPresent(self.ren)
        sdl2.SDL_DestroyTexture(self.background)
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
