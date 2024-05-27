import sdl2
import sdl2.ext


class Game:
    def __init__(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"Cannot initialize SDL2: {sdl2.SDL_GetError().decode('utf-8')}")
        self.window = sdl2.ext.Window('Game', size=(800, 600))
        self.window.show()
        self.running = True

    def run(self):
        while self.running:
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    self.running = False
        sdl2.SDL_QUIT()

    def update(self):
        return 0;

    def render(self):
        self.window.refresh()


if __name__ == '__main__':
    game = Game()
    game.run()
