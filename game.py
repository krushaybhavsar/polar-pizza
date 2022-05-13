from matplotlib.pyplot import get
import pygame, sys, math, random
from settings import *

class PolarPizza:

    def __init__(self):
        # screen
        pygame.display.set_caption("Polar Pizza")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # game
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'playing'
        # polar graph
        self.petal_num = random.randint(2, 5)
        self.equation_type = random.choice(['cos', 'sin'])
        self.graph_scale_factor = MAX_PATH_SCALE
        self.delivery_house_points = []
        # pizza
        self.pizza_theta = 0.0
        self.pizza_coordinates = (0, 0)
        # images
        self.grass_bg = pygame.image.load('images/grass.jpg')
        self.house_img = pygame.transform.scale(pygame.image.load('images/house.png'), (60, 60))
        self.pizza_img = pygame.transform.scale(pygame.image.load('images/pizza.png'), (40, 40))
        self.pizza_shop = pygame.transform.scale(pygame.image.load('images/pizza-shop.png'), (90, 90))

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
        t = self.pizza_theta
        r = self.get_r(t, self.graph_scale_factor)
        self.pizza_coordinates = (r * math.cos(t), r * math.sin(t))
        self.pizza_theta = (self.pizza_theta % (2 * math.pi)) + (math.pi / 180)

    # this mess doesnt work lol
    # def get_pizza_increment(self, t):
    #     x = 0
    #     y = 0
    #     if self.equation_type == 'cos':
    #         # a(-n*sin(nx)cos(x) - cos(nx)sin(x))
    #         x = self.graph_scale_factor * (-self.petal_num * math.sin(self.petal_num * t) * math.cos(t) - math.cos(self.petal_num * t) * math.sin(t))
    #         # a(-n*sin(nx)sin(x) + cos(nx)cos(x))
    #         y = self.graph_scale_factor * (-self.petal_num * math.sin(self.petal_num * t) * math.sin(t) + math.cos(self.petal_num * t) * math.cos(t))
    #     elif self.equation_type == 'sin':
    #         # a(n*cos(nx)cos(x) - sin(nx)sin(x))
    #         x = self.graph_scale_factor * (self.petal_num * math.cos(self.petal_num * t) * math.cos(t) - math.sin(self.petal_num * t) * math.sin(t))
    #         # a(n*cos(nx)sin(x) + sin(nx)cos(x))
    #         y = self.graph_scale_factor * (self.petal_num * math.cos(self.petal_num * t) * math.sin(t) + math.sin(self.petal_num * t) * math.cos(t))
    #     return math.sqrt(x**2 + y**2)

    def draw_screen(self):
        self.screen.blit(self.grass_bg, (0, 0))
        self.draw_delivery_path()
        self.draw_houses()
        self.screen.blit(self.pizza_shop, (WIDTH//2 - self.pizza_shop.get_width()//2, HEIGHT//2 - self.pizza_shop.get_height()//2))
        self.draw_pizza()
        pygame.display.update()

    def get_r(self, theta, scale):
        if self.equation_type == 'cos':
            return scale * math.cos(self.petal_num * theta)
        elif self.equation_type == 'sin':
            return scale * math.sin(self.petal_num * theta)

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
        self.graph_scale_factor = 0.75 * ps # scale down to 75% of max size

        # draw path, then houses
        while theta < 2 * math.pi:
            r = self.get_r(theta, self.graph_scale_factor)
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            if abs(abs(r) - self.graph_scale_factor) < PETAL_TIP_ERROR and len(self.delivery_house_points) < HOUSE_THRESHOLD: # add to list of houses if point is tip of petal
                self.delivery_house_points.append((x + WIDTH//2, y + HEIGHT//2))
                pass
            else:
                pygame.draw.circle(self.screen, PATH_COLOR, (x + WIDTH//2, y + HEIGHT//2), PATH_STROKE_WIDTH)
            theta += (1 / DELIVERY_PATH_RESOLUTION)

    def draw_houses(self):
        for tip in self.delivery_house_points:
            self.screen.blit(self.house_img, (tip[0] - self.house_img.get_width()//2, tip[1] - self.house_img.get_height()//2)) 

    def draw_pizza(self):
        self.screen.blit(self.pizza_img, (self.pizza_coordinates[0] + WIDTH//2 - self.pizza_img.get_width()//2, self.pizza_coordinates[1] + HEIGHT//2 - self.pizza_img.get_height()//2))
        

if __name__ == "__main__":
    game = PolarPizza()
    game.run()