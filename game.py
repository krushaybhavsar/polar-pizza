import pygame, sys, math, random
from settings import *

class PolarPizza:

    def __init__(self):
        pygame.display.set_caption("Polar Pizza")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'playing'
        self.temp_n = random.randint(2, 8)
        # images
        self.grass_bg = pygame.image.load('images/grass.jpg')

    def run(self):
        while self.running:
            if self.state == 'playing':
                self.check_events()
                self.update()
                self.draw_screen()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
    
    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass

    def draw_screen(self):
        self.screen.blit(self.grass_bg, (0, 0))
        self.draw_delivery_path()
        pygame.display.update()

    def get_r(self, theta, scale):
        n = self.temp_n
        return scale * math.cos(n * theta)

    def draw_delivery_path(self):
        ps = MAX_PATH_SCALE
        theta = 0
        r = 0
        x = 0
        y = 0

        # find path scale factor
        while theta < 2 * math.pi:
            r = self.get_r(theta, ps)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            while x + WIDTH//2 > WIDTH or x + WIDTH//2 < 0 or y + HEIGHT//2 > HEIGHT or y + HEIGHT//2 < 0:
                ps -= 1
                r = self.get_r(theta, ps)
                x = r * math.cos(theta)
                y = r * math.sin(theta)
            theta += math.pi / 180
        theta = 0
        ps *= 0.75 # scale down to 75% of max size

        # draw path
        while theta < 2 * math.pi:
            r = self.get_r(theta, ps)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            pygame.draw.circle(self.screen, RED, (x + WIDTH//2, y + HEIGHT//2), PATH_STROKE_WIDTH)
            theta += (1 / DELIVERY_PATH_RESOLUTION)
        

if __name__ == "__main__":
    game = PolarPizza()
    game.run()