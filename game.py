import pygame, sys, math, random
from settings import *
import numpy as np

class PolarPizza:

    def __init__(self):
        # screen
        pygame.display.set_caption("Polar Pizza")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # game
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'playing'
        self.mouse_pos = (0, 0)
        # polar graph
        self.petal_num = random.randint(2, 5)
        self.constants = np.random.randint(1, 10, 2)
        self.equation_type = random.choice(['cos', 'sin', 'limacon-cos', 'limacon-sin'])#, 'lemniscate-cos', 'lemniscate-sin'])
        # self.equation_type = 'limacon-sin'
        self.equation_sign = np.random.choice([-1, 1])
        self.period = 2 * math.pi
        self.graph_scale_factor = MAX_PATH_SCALE
        self.delivery_house_points = []
        # pizza
        self.pizza_theta = 0.0
        self.pizza_coordinates = (0, 0)
        self.pizza_moving = True
        # images
        self.grass_bg = pygame.image.load('images/grass.jpg')
        self.house_img = pygame.transform.scale(pygame.image.load('images/house.png'), (55, 55))
        self.pizza_img = pygame.transform.scale(pygame.image.load('images/pizza.png'), (40, 40))
        self.pizza_shop = pygame.transform.scale(pygame.image.load('images/pizza-shop.png'), (80, 80))
        # fonts
        self.font = pygame.font.Font("fonts/roboto.ttf", 50)
        self.font_medium = pygame.font.Font("fonts/roboto.ttf", 34)
        self.font_small = pygame.font.Font("fonts/roboto.ttf", 30)
        self.font_btn = pygame.font.Font("fonts/roboto.ttf", 32)
        # answer box
        self.input_text = ""
        self.cursor_blink_count = 0
        self.cursor_blink_state = False
        self.over_text_limit = False
        self.question = "Find the number of houses the pizza can get."
        self.units = "minutes"
        self.question_type = "houses"
        self.check_btn_hover = False

        self.define_graph()


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
        events = pygame.event.get()
        self.mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    self.over_text_limit = False
                # check if key is a number
                if not self.over_text_limit and (event.key >= pygame.K_0 and event.key <= pygame.K_9):
                    self.input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.check_btn_hover:
                    self.pizza_moving = True
                    self.check_answer()

    def update(self):
        if self.pizza_moving and self.pizza_theta < 2 * math.pi:
            t = self.pizza_theta
            r = self.get_r(t, self.graph_scale_factor)
            self.pizza_coordinates = (r * math.cos(t) + AXIS_OFFSET[0], r * math.sin(t) + AXIS_OFFSET[1])
            self.pizza_theta = self.pizza_theta + (math.pi / 180)

    def draw_screen(self):
        self.screen.blit(self.grass_bg, (0, 0))
        self.draw_delivery_path()
        self.draw_pizza()
        self.draw_houses()
        self.screen.blit(self.pizza_shop, (WIDTH//2 - self.pizza_shop.get_width()//2 + AXIS_OFFSET[0], HEIGHT//2 - self.pizza_shop.get_height()//2 + AXIS_OFFSET[1]))
        self.draw_delivery_info()
        self.draw_answer_box()
        pygame.display.update()

    def check_answer(self):
        ans = float(self.input_text)
        print("you stupid")

    def get_r(self, theta, scale):
        if self.equation_type == 'cos':
            return scale * math.cos(self.petal_num * theta)
        elif self.equation_type == 'sin':
            return scale * math.sin(self.petal_num * theta)
        elif self.equation_type == 'limacon-cos':
            return scale * (self.constants[0] + self.equation_sign * self.constants[1] * math.cos(theta))
        elif self.equation_type == 'limacon-sin':
            return scale * (self.constants[0] + self.equation_sign * self.constants[1] * math.sin(theta))
        # elif self.equation_type == 'lemniscate-cos':
        #     return scale * (np.sqrt(abs(np.power(self.constants[0], 2) * math.cos(2 * theta))))
        # elif self.equation_type == 'lemniscate-sin':
        #     return scale * (np.sqrt(abs(np.power(self.constants[0], 2) * math.sin(2 * theta))))
            
    
    def get_equation_string(self):
        if 'cos' == self.equation_type or 'sin' == self.equation_type:
            return f"r = {self.graph_scale_factor}∙{self.equation_type}({self.petal_num}θ)"
        elif 'limacon-cos' == self.equation_type or 'limacon-sin' == self.equation_type:
            if self.equation_sign == 1:
                return f"r = {self.graph_scale_factor}∙({self.constants[0]} + {self.constants[1]}∙{self.equation_type[-3:]}(θ))"
            else:
                return f"r = {self.graph_scale_factor}∙({self.constants[0]} - {self.constants[1]}∙{self.equation_type[-3:]}(θ))"

    def define_graph(self):
        if 'cos' == self.equation_type or 'sin' == self.equation_type:
            ps = min(WIDTH//2, HEIGHT//2)
            if self.petal_num % 2 == 0:
                num_petals = self.petal_num * 2
                house_period = 2 * math.pi / num_petals
            else:
                num_petals = self.petal_num
                house_period = math.pi / num_petals
        
        elif 'limacon-cos' == self.equation_type:
            # y, x-neg, x-pos
            # 3 + 6 cos(theta)
            critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
            if self.constants[0] == self.constants[1]:
                # Handle Cardioid case
                ps = min((WIDTH//2) // critical_vals[2], (HEIGHT//2) // critical_vals[0])
            else:
                ps = min((WIDTH//2) // critical_vals[2], (WIDTH//2) // critical_vals[1], (HEIGHT//2) // critical_vals[0])

        elif 'limacon-sin' == self.equation_type:
            # x, y-neg, y-pos
            # 3 + 6 cos(theta)
            critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
            if self.constants[0] == self.constants[1]:
                # Handle Cardioid case
                ps = min((HEIGHT//2) // critical_vals[2], (WIDTH//2) // critical_vals[0])
            else:
                ps = min((HEIGHT//2) // critical_vals[2], (HEIGHT//2) // critical_vals[1], (WIDTH//2) // critical_vals[0])

        self.graph_scale_factor = round(0.6 * ps) # scale down to 60% of max size

        if 'cos' == self.equation_type:
            for i in range(0, num_petals):
                theta = i * house_period
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))

        elif 'sin' == self.equation_type:
            for i in range(num_petals):
                theta = i * house_period + house_period / 2
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))

        elif 'limacon-cos' == self.equation_type or 'limacon-sin' == self.equation_type:
            key_points = [0, math.pi/2, math.pi, 3*math.pi/2]
            for theta in key_points:
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))

    def draw_delivery_path(self):
        theta = 0
        r = 0
        x = 0
        y = 0
        # find path scale factor

        # if 'cos' == self.equation_type or 'sin' == self.equation_type:
        #     ps = min(WIDTH//2, HEIGHT//2)
        #     num_petals = self.petal_num * 2 if self.petal_num % 2 == 0 else self.petal_num
        #     house_period = 2 * math.pi / num_petals
        #     print(num_petals, house_period)
        #     for i in range(num_petals):
        #         theta = i * house_period
        #         r = self.get_r(theta, self.graph_scale_factor)
        #         x = r * math.cos(theta)
        #         y = r * math.sin(theta)
        #         print(theta, r, x, y)
        #         self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))

        #     print(self.delivery_house_points)

        # elif 'limacon-cos' == self.equation_type:
        #     # y, x-neg, x-pos
        #     # 3 + 6 cos(theta)
        #     critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
        #     if self.constants[0] == self.constants[1]:
        #         # Handle Cardioid case
        #         ps = min((WIDTH//2) // critical_vals[2], (HEIGHT//2) // critical_vals[0])
        #     else:
        #         ps = min((WIDTH//2) // critical_vals[2], (WIDTH//2) // critical_vals[1], (HEIGHT//2) // critical_vals[0])

        #     # Calculate Key Points

        #     key_points = [0, math.pi/2, math.pi, 3*math.pi/2]
        #     for theta in key_points:
        #         r = self.get_r(theta, self.graph_scale_factor)
        #         x = r * math.cos(theta)
        #         y = r * math.sin(theta)
        #         self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))


        # elif 'limacon-sin' == self.equation_type:
        #     # x, y-neg, y-pos
        #     # 3 + 6 cos(theta)
        #     critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
        #     if self.constants[0] == self.constants[1]:
        #         # Handle Cardioid case
        #         ps = min((HEIGHT//2) // critical_vals[2], (WIDTH//2) // critical_vals[0])
        #     else:
        #         ps = min((HEIGHT//2) // critical_vals[2], (HEIGHT//2) // critical_vals[1], (WIDTH//2) // critical_vals[0])

        #     key_points = [0, math.pi/2, math.pi, 3*math.pi/2]
        #     for theta in key_points:
        #         r = self.get_r(theta, self.graph_scale_factor)
        #         x = r * math.cos(theta)
        #         y = r * math.sin(theta)
        #         self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))

        
        # while theta < 2 * math.pi:
        #     r = self.get_r(theta, ps)
        #     x = r * math.cos(theta)
        #     y = r * math.sin(theta)
        #     while x + WIDTH//2 > WIDTH or x + WIDTH//2 < 0 or y + HEIGHT//2 > HEIGHT or y + HEIGHT//2 < 0:
        #         ps -= 1
        #         r = self.get_r(theta, ps)
        #         x = r * math.cos(theta)
        #         y = r * math.sin(theta)
        #     theta += math.pi / 180
        # self.graph_scale_factor = round(0.6 * ps) # scale down to 60% of max size

        # draw path, then houses
        while theta < 2 * math.pi:
            r = self.get_r(theta, self.graph_scale_factor)
            x = r * math.cos(theta)
            y = r * math.sin(theta)

            # if abs(abs(r) - self.graph_scale_factor) < PETAL_TIP_ERROR and len(self.delivery_house_points) < HOUSE_THRESHOLD: # add to list of houses if point is tip of petal
            #     self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))
            #     pass
            # else:
            pygame.draw.circle(self.screen, PATH_COLOR, (x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]), PATH_STROKE_WIDTH)
            theta += (1 / DELIVERY_PATH_RESOLUTION)

    def draw_houses(self):
        for tip in self.delivery_house_points:
            self.screen.blit(self.house_img, (tip[0] - self.house_img.get_width()//2, tip[1] - self.house_img.get_height()//2)) 
        
    def draw_pizza(self):
        self.screen.blit(self.pizza_img, (self.pizza_coordinates[0] + WIDTH//2 - self.pizza_img.get_width()//2, self.pizza_coordinates[1] + HEIGHT//2 - self.pizza_img.get_height()//2))

    def draw_delivery_info(self):
        self.screen.blit(self.font.render(self.get_equation_string(), True, INFO_FONT_COLOR), (40, 30))

    def draw_answer_box(self):
        pygame.draw.rect(self.screen, AB_BG_COLOR, (0 + AB_HORIZONTAL_PADDING, HEIGHT - AB_HEIGHT, WIDTH - 2*AB_HORIZONTAL_PADDING, AB_HEIGHT), border_top_left_radius=AB_BORDER_RADIUS, border_top_right_radius=AB_BORDER_RADIUS)
        self.screen.blit(self.font_small.render(self.question, True, INFO_FONT_COLOR), (AB_HORIZONTAL_PADDING + 40, HEIGHT - AB_HEIGHT + 25))
        self.screen.blit(self.font_medium.render("Answer: " + self.input_text + " " + self.units, True, INFO_FONT_COLOR), (AB_HORIZONTAL_PADDING + 40, HEIGHT - AB_HEIGHT + 70))       
        if self.cursor_blink_count % CURSOR_BLINK_RATE == 0:
            self.cursor_blink_state = not self.cursor_blink_state
        self.cursor_blink_count += 1
        if self.cursor_blink_state:
            self.screen.blit(self.font_medium.render('|', True, INFO_FONT_COLOR), (AB_HORIZONTAL_PADDING + self.font_medium.size("Answer: " + self.input_text)[0] + 36, HEIGHT - AB_HEIGHT - 4 + 70))
        if self.font_medium.size("Answer: " + self.input_text + " " + self.units)[0] + AB_HORIZONTAL_PADDING + 80 > WIDTH - 2*AB_HORIZONTAL_PADDING:
            self.over_text_limit = True
        check_btn_coordinates = (AB_HORIZONTAL_PADDING + WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH - 40, HEIGHT - AB_HEIGHT//2 - CHECK_BUTTON_HEIGHT//2)
        btn_color = CHECK_BUTTON_COLOR
        font_color = CB_FONT_COLOR
        if check_btn_coordinates[0] < self.mouse_pos[0] < check_btn_coordinates[0] + CHECK_BUTTON_WIDTH and check_btn_coordinates[1] < self.mouse_pos[1] < check_btn_coordinates[1] + CHECK_BUTTON_HEIGHT and self.input_text != "":
            self.check_btn_hover = True
            btn_color = CHECK_BUTTON_HOVER_COLOR
            font_color = CB_HOVER_FONT_COLOR
        else:
            self.check_btn_hover = False
        pygame.draw.rect(self.screen, btn_color, (check_btn_coordinates[0], check_btn_coordinates[1], CHECK_BUTTON_WIDTH, CHECK_BUTTON_HEIGHT), border_top_left_radius=CB_BR, border_top_right_radius=CB_BR, border_bottom_left_radius=CB_BR, border_bottom_right_radius=CB_BR)
        self.screen.blit(self.font_btn.render("Check", True, font_color), (AB_HORIZONTAL_PADDING + WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH + CHECK_BUTTON_WIDTH//2 - self.font_btn.size("Check")[0]//2 - 40, HEIGHT - AB_HEIGHT//2 - self.font_btn.size("Check")[1]//2))

if __name__ == "__main__":
    pygame.init()
    game = PolarPizza()
    game.run()