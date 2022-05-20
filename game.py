import pygame, sys, math, random
from matplotlib.pyplot import draw
import pygame, sys, math, random, threading
from settings import *
import numpy as np
import sympy as sym

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
        self.loading = True
        self.info_message = ""
        # polar graph
        self.petal_num = random.randint(4, 4)
        self.constants = np.random.randint(1, 10, 2)
        self.equation_type = random.choice(['cos', 'sin', 'limacon-cos', 'limacon-sin'])#, 'lemniscate-cos', 'lemniscate-sin'])
        # self.equation_type = 'sin'
        self.equation_sign = np.random.choice([-1, 1])
        self.graph_scale_factor = MAX_PATH_SCALE
        self.delivery_house_points = []
        self.delivery_house_thetas = []
        # pizza
        self.pizza_theta = 0.0
        self.initial_pizza_theta = 0.0
        self.pizza_coordinates = (AXIS_OFFSET[0], AXIS_OFFSET[1])
        self.pizza_moving = False
        self.pizza_max_theta = 2 * math.pi
        # images
        self.grass_bg = pygame.image.load('images/grass.jpg')
        self.house_img = pygame.transform.scale(pygame.image.load('images/house.png'), (55, 55))
        self.pizza_img = pygame.transform.scale(pygame.image.load('images/pizza.png'), (40, 40))
        self.pizza_shop = pygame.transform.scale(pygame.image.load('images/pizza-shop.png'), (85, 85))
        self.correct_img = pygame.transform.scale(pygame.image.load('images/correct.png'), (40, 40))
        self.incorrect_img = pygame.transform.scale(pygame.image.load('images/incorrect.png'), (40, 40))
        # fonts
        self.font = pygame.font.Font("fonts/roboto.ttf", 50)
        self.font_medium = pygame.font.Font("fonts/roboto.ttf", 32)
        self.font_small = pygame.font.Font("fonts/roboto.ttf", 28)
        self.font_btn = pygame.font.Font("fonts/roboto.ttf", 32)
        # answer box
        self.input_text = ""
        self.cursor_blink_count = 0
        self.cursor_blink_state = False
        self.over_text_limit = False
        self.question = "Find the minimum distance the pizza has to travel to deliver to all the houses and return home. Round to the nearest whole number."
        self.units = "meters"
        self.check_btn_enabled = False
        self.button_hovered = False
        self.answer_state = "none"
        self.input_enabled = True
        self.correct_ans = -1
        # equation
        self.t = sym.Symbol('t', real=True, nonnegative=True)
        self.domain = sym.Interval(0, math.inf)

        # graphing
        self.steps_scaling_factor = 1
        self.define_graph()
        self.time_low, self.time_high, self.time_end = self.generate_time_bounds()
        
        # answer
        self.correct_ans_thread = threading.Thread(target=self.get_correct_ans)
        self.correct_ans_thread.start()
        self.correct_ans = -1

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
            if self.input_enabled and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                    self.over_text_limit = False
                if not self.over_text_limit and (event.key >= pygame.K_0 and event.key <= pygame.K_9 or pygame.K_PERIOD):
                    if str(event.unicode) in "0123456789.":
                        self.input_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.check_btn_enabled and self.button_hovered:
                    self.pizza_moving = True
                    self.pizza_theta = self.initial_pizza_theta
                    self.time = self.time_low
                    self.check_answer()

    def scaling_equation(self, time):
        max_scale_constant = 100
        exponential_constant = 0.01 * (self.time_high - self.time_end)
        return (max_scale_constant + 1) - max_scale_constant * np.exp(-exponential_constant * (time - self.time_low))

    def update(self):
        if self.pizza_moving:
            if self.time < self.time_end and self.pizza_theta < self.pizza_max_theta and self.pizza_theta > self.initial_pizza_theta - self.period:
                self.increment = (self.time_end - self.time_low) / (self.steps_scaling_factor * self.initial_scaling_factor)
                self.steps_scaling_factor = self.scaling_equation(self.time)#*= 1.0001
                theta = sym.integrate(self.dthetaT, (self.t, self.time, self.time + self.increment)) + self.pizza_theta # Need to simply calculate theta by integrating dtheta/dt from time_low to time and adding to initial pizza theta
                # print(self.steps_scaling_factor, theta)
                # print(self.time, theta)
                r = self.get_r(theta, self.graph_scale_factor)
                self.pizza_coordinates = (r * math.cos(theta) + AXIS_OFFSET[0], -(r * math.sin(theta)) + AXIS_OFFSET[1])
                self.pizza_theta = theta
                # self.pizza_theta = self.pizza_theta + (math.pi / 180)
                self.time += self.increment
            else:
                self.pizza_moving = False

    def draw_screen(self):
        self.screen.blit(self.grass_bg, (0, 0))
        self.draw_delivery_path()
        self.draw_pizza()
        self.draw_houses()
        self.screen.blit(self.pizza_shop, (WIDTH//2 - self.pizza_shop.get_width()//2 + AXIS_OFFSET[0], HEIGHT//2 - self.pizza_shop.get_height()//2 + AXIS_OFFSET[1] + 5))
        self.draw_delivery_info()
        self.draw_answer_box()
        pygame.display.update()

    def check_answer(self):
        try:
            self.correct_ans_thread.join()
            ans = int(self.input_text)
            if self.units == "houses":
                pass
            elif self.units == "meters":
                if ans == self.correct_ans:
                    self.answer_state = "correct"
                    self.input_enabled = False
                else:
                    self.answer_state = "incorrect"
                    self.input_text = ""
        except:
            self.info_message = "Invalid input!"

    def get_correct_ans(self):
        if self.units == "houses":
            self.info_message = "Calculating max number of houses..."
            pass
        elif self.units == "meters":
            self.info_message = "Calculating distance..."
            self.correct_ans = self.calc_distance()
        self.info_message = ""
        print("Correct answer: " + str(self.correct_ans))

    def calc_distance(self):
        n = sym.Symbol("n")
        r = None
        if self.equation_type == 'cos':
            r = self.graph_scale_factor * sym.cos(self.petal_num * n)
        elif self.equation_type == 'sin':
            r = self.graph_scale_factor * sym.sin(self.petal_num * n)
        elif self.equation_type == 'limacon-cos':
            r = self.graph_scale_factor * (self.constants[0] + self.equation_sign * self.constants[1] * sym.cos(n))
        elif self.equation_type == 'limacon-sin':
            r = self.graph_scale_factor * (self.constants[0] + self.equation_sign * self.constants[1] * sym.sin(n))
        x_coord = r * sym.cos(n)
        y_coord = r * sym.sin(n)
        dxdtheta = sym.diff(x_coord, n)
        dydtheta = sym.diff(y_coord, n)
        length = sym.integrate(sym.sqrt(sym.Pow(dxdtheta, 2) + sym.Pow(dydtheta, 2)), (n, self.initial_pizza_theta, self.pizza_max_theta)).evalf()
        return round(length)

    def calc_area(self):
        self.info_message = "Calculating area..."
        a = sym.Symbol('a')
        ans = 0.0
        if self.equation_type == 'cos':
            ans = sym.integrate((self.graph_scale_factor * sym.cos(self.petal_num * a))**2, (a, 0, self.pizza_max_theta - self.initial_pizza_theta))
        elif self.equation_type == 'sin':
            ans = sym.integrate((self.graph_scale_factor * sym.sin(self.petal_num * a))**2, (a, 0, self.pizza_max_theta - self.initial_pizza_theta))
        elif self.equation_type == 'limacon-cos':
            ans = sym.integrate((self.graph_scale_factor * (self.constants[0] + self.equation_sign * self.constants[1] * sym.cos(a)))**2, (a, 0, self.pizza_max_theta - self.initial_pizza_theta))
        elif self.equation_type == 'limacon-sin':
            ans = sym.integrate((self.graph_scale_factor * (self.constants[0] + self.equation_sign * self.constants[1] * sym.sin(a)))**2, (a, 0, self.pizza_max_theta - self.initial_pizza_theta))
        self.info_message = ""
        return 0.5*ans

    def get_r(self, theta, scale):
        if self.equation_type == 'cos':
            return scale * math.cos(self.petal_num * theta)
        elif self.equation_type == 'sin':
            return scale * math.sin(self.petal_num * theta)
        elif self.equation_type == 'limacon-cos':
            return scale * (self.constants[0] + self.equation_sign * self.constants[1] * math.cos(theta))
        elif self.equation_type == 'limacon-sin':
            return scale * (self.constants[0] + self.equation_sign * self.constants[1] * math.sin(theta))
            
    def get_equation_string(self):
        if 'cos' == self.equation_type or 'sin' == self.equation_type:
            return f"r = {self.graph_scale_factor}∙{self.equation_type}({self.petal_num}θ)"
        elif 'limacon-cos' == self.equation_type or 'limacon-sin' == self.equation_type:
            if self.equation_sign == 1:
                return f"r = {self.graph_scale_factor}∙({self.constants[0]} + {self.constants[1]}∙{self.equation_type[-3:]}(θ))"
            else:
                return f"r = {self.graph_scale_factor}∙({self.constants[0]} - {self.constants[1]}∙{self.equation_type[-3:]}(θ))"

    def generate_velocity(self):
        dtheta_coeff = np.random.randint(COEFF_LOWER_BOUND, COEFF_UPPER_BOUND, size=8)
        self.dthetaT = 0
        for i in range(len(dtheta_coeff)):
            self.dthetaT += dtheta_coeff[i] * self.t**i

    def generate_time_bounds(self):
        self.info_message = "Generating time bounds..."
        num_lower = 0
        num_upper = 0

        low = 0
        high = 0

        while low >= high:
            self.generate_velocity()
            
            self.theta_equation = sym.integrate(self.dthetaT, self.t)

            lower_time = sym.solveset(self.theta_equation - self.initial_pizza_theta, self.t, domain=self.domain)
            upper_time = sym.solveset(self.theta_equation - self.pizza_max_theta, self.t, domain=self.domain)

            try:
                lower_time = list(lower_time)
                upper_time = list(upper_time)
            except:
                print("Found an impossible equation to solve... Trying again...")
                continue

            num_lower = len(lower_time)
            num_upper = len(upper_time)

            if num_lower > 0 and num_upper > 0:
                low = float(lower_time[0])
                high = float(upper_time[0]) 

        duration = (high - low) / 2
        end = np.random.uniform(low + duration / 2, high)

        if self.units == "meters":
            end = high

        self.pizza_max_theta = self.theta_equation.subs(self.t, end)
        self.info_message = ""

        return low, high, end

    def calculate_answer(self):
        count = 0
        for point in self.delivery_house_thetas:
            if point > self.initial_pizza_theta and point < self.pizza_max_theta:
                count += 1
        return count

    def draw_delivery_path(self):
        theta = 0
        r = 0
        x = 0
        y = 0
        while theta < self.period:
            r = self.get_r(theta, self.graph_scale_factor)
            x = r * math.cos(theta)
            y = -r * math.sin(theta)
            pygame.draw.circle(self.screen, PATH_COLOR, (x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]), PATH_STROKE_WIDTH)
            theta += (1 / DELIVERY_PATH_RESOLUTION)

    def define_graph(self):
        self.info_message = "Drawing graph..."
        if 'cos' == self.equation_type:
            ps = min(WIDTH//2, HEIGHT//2)
            if self.petal_num % 2 == 0:
                self.period = 2 * math.pi
                num_petals = self.petal_num * 2
                house_period = 2 * math.pi / num_petals
                self.initial_pizza_theta = house_period / 2
                self.pizza_max_theta = self.initial_pizza_theta + self.period
                self.initial_scaling_factor = 1000
            else:
                self.period = math.pi
                num_petals = self.petal_num
                house_period = math.pi / num_petals
                self.initial_pizza_theta = house_period / 2
                self.pizza_max_theta = self.initial_pizza_theta + self.period
                self.initial_scaling_factor = 1000

        if 'sin' == self.equation_type:
            ps = min(WIDTH//2, HEIGHT//2)
            if self.petal_num % 2 == 0:
                self.period = 2 * math.pi
                num_petals = self.petal_num * 2
                house_period = 2 * math.pi / num_petals
                self.initial_pizza_theta = 0
                self.pizza_max_theta = self.initial_pizza_theta + self.period
                self.initial_scaling_factor = 1000
            else:
                self.period = math.pi
                num_petals = self.petal_num
                house_period = math.pi / num_petals
                self.initial_pizza_theta = 0
                self.pizza_max_theta = self.initial_pizza_theta + self.period
                self.initial_scaling_factor = 1000
        
        elif 'limacon-cos' == self.equation_type:
            # y, x-neg, x-pos
            # 3 + 6 cos(theta)
            self.period = 2 * math.pi
            self.initial_pizza_theta = 0 if self.equation_sign < 0 else math.pi
            self.pizza_max_theta = self.initial_pizza_theta + self.period
            self.initial_scaling_factor = 100
            critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
            if self.constants[0] == self.constants[1]:
                # Handle Cardioid case
                ps = min((WIDTH//2) // critical_vals[2], (HEIGHT//2) // critical_vals[0])
            else:
                ps = min((WIDTH//2) // critical_vals[2], (WIDTH//2) // critical_vals[1], (HEIGHT//2) // critical_vals[0])

        elif 'limacon-sin' == self.equation_type:
            # x, y-neg, y-pos
            # 3 + 6 cos(theta)
            self.period = 2 * math.pi
            self.initial_pizza_theta = math.pi / 2 if self.equation_sign < 0 else 3 * math.pi / 2
            self.pizza_max_theta = self.initial_pizza_theta + self.period
            self.initial_scaling_factor = 100
            critical_vals = list(map(abs, [self.constants[0], self.constants[0] - self.constants[1], self.constants[0] + self.constants[1]]))
            if self.constants[0] == self.constants[1]:
                # Handle Cardioid case
                ps = min((HEIGHT//2) // critical_vals[2], (WIDTH//2) // critical_vals[0])
            else:
                ps = min((HEIGHT//2) // critical_vals[2], (HEIGHT//2) // critical_vals[1], (WIDTH//2) // critical_vals[0])

        self.graph_scale_factor = round(0.6 * ps) # scale down to 60% of max size

        if 'cos' == self.equation_type:
            # print(house_period)
            # self.pizza_theta = house_period / 2
            for i in range(num_petals):
                theta = i * house_period
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = -r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))
                self.delivery_house_thetas.append(theta)

        elif 'sin' == self.equation_type:
            # self.pizza_theta = 0
            for i in range(num_petals):
                theta = i * house_period + house_period / 2
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = -r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))
                self.delivery_house_thetas.append(theta)

        elif 'limacon-cos' == self.equation_type or 'limacon-sin' == self.equation_type:
            key_points = [0, math.pi/2, math.pi, 3*math.pi/2]
            for theta in key_points:
                r = self.get_r(theta, self.graph_scale_factor)
                x = r * math.cos(theta)
                y = -r * math.sin(theta)
                self.delivery_house_points.append((x + WIDTH//2 + AXIS_OFFSET[0], y + HEIGHT//2 + AXIS_OFFSET[1]))
                self.delivery_house_thetas.append(theta)
        
        if self.units == "meters":
            self.correct_ans = self.calc_distance()
        elif self.units == "houses":
            pass

        self.info_message = ""

    def draw_delivery_path(self):
        theta = 0
        r = 0
        x = 0
        y = 0
        while theta < self.period:
            r = self.get_r(theta, self.graph_scale_factor)
            x = r * math.cos(theta)
            y = -r * math.sin(theta)
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
        self.draw_text(text=self.info_message, color=INFO_FONT_COLOR, font=self.font_small, rect=pygame.Rect(AB_HORIZONTAL_PADDING + 40, HEIGHT - AB_HEIGHT - 35, WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH - 75, AB_HEIGHT), aa=True)
        pygame.draw.rect(self.screen, AB_BG_COLOR, (0 + AB_HORIZONTAL_PADDING, HEIGHT - AB_HEIGHT, WIDTH - 2*AB_HORIZONTAL_PADDING, AB_HEIGHT), border_top_left_radius=AB_BORDER_RADIUS, border_top_right_radius=AB_BORDER_RADIUS)
        self.draw_text(text=self.question, color=INFO_FONT_COLOR, font=self.font_small, rect=pygame.Rect(AB_HORIZONTAL_PADDING + 40, HEIGHT - AB_HEIGHT + 25, WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH - 75, AB_HEIGHT), aa=True)
        self.screen.blit(self.font_medium.render("Answer: " + self.input_text + " " + self.units, True, INFO_FONT_COLOR), (AB_HORIZONTAL_PADDING + 40, HEIGHT - 60))       
        if self.cursor_blink_count % CURSOR_BLINK_RATE == 0:
            self.cursor_blink_state = not self.cursor_blink_state
        self.cursor_blink_count += 1
        if self.cursor_blink_state and self.input_enabled:
            self.screen.blit(self.font_medium.render('|', True, INFO_FONT_COLOR), (AB_HORIZONTAL_PADDING + self.font_medium.size("Answer: " + self.input_text)[0] + 36, HEIGHT - 4 - 60))
        if self.font_medium.size("Answer: " + self.input_text + " " + self.units)[0] > self.font_small.size(self.question)[0]:
            self.over_text_limit = True
        icon_coord = (AB_HORIZONTAL_PADDING + self.font_medium.size("Answer: " + self.input_text + " " + self.units)[0] + 58, HEIGHT - 60 - 3)
        if self.answer_state == "correct":
            self.screen.blit(self.correct_img, icon_coord)
            self.screen.blit(self.font_medium.render("Correct!", True, GREEN), (icon_coord[0] + 52, HEIGHT - 60))       
        elif self.answer_state == "incorrect":
            self.screen.blit(self.incorrect_img, icon_coord)
            self.screen.blit(self.font_medium.render("Incorrect! Try again...", True, RED), (icon_coord[0] + 52, HEIGHT - 60))       
        check_btn_coordinates = (AB_HORIZONTAL_PADDING + WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH - 40, HEIGHT - AB_HEIGHT//2 - CHECK_BUTTON_HEIGHT//2)
        btn_color = CHECK_BUTTON_COLOR
        font_color = CB_FONT_COLOR
        self.button_hovered = check_btn_coordinates[0] < self.mouse_pos[0] < check_btn_coordinates[0] + CHECK_BUTTON_WIDTH and check_btn_coordinates[1] < self.mouse_pos[1] < check_btn_coordinates[1] + CHECK_BUTTON_HEIGHT 
        if self.input_text != "":
            self.check_btn_enabled = True
            btn_color = CHECK_BUTTON_ENABLED_COLOR
            font_color = CB_HOVER_FONT_COLOR
            if self.button_hovered:
                btn_color = CHECK_BUTTON_HOVER_COLOR
        else:
            self.check_btn_enabled = False
        pygame.draw.rect(self.screen, btn_color, (check_btn_coordinates[0], check_btn_coordinates[1], CHECK_BUTTON_WIDTH, CHECK_BUTTON_HEIGHT), border_top_left_radius=CB_BR, border_top_right_radius=CB_BR, border_bottom_left_radius=CB_BR, border_bottom_right_radius=CB_BR)
        self.screen.blit(self.font_btn.render("Check", True, font_color), (AB_HORIZONTAL_PADDING + WIDTH - 2*AB_HORIZONTAL_PADDING - CHECK_BUTTON_WIDTH + CHECK_BUTTON_WIDTH//2 - self.font_btn.size("Check")[0]//2 - 40, HEIGHT - AB_HEIGHT//2 - self.font_btn.size("Check")[1]//2))

    def draw_text(self, text, color, rect, font, aa=False, bkg=None):
        y = rect.top
        lineSpacing = -2
        fontHeight = font.size("Tg")[1] + 3
        while text:
            i = 1
            if y + fontHeight > rect.bottom:
                break
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)
            self.screen.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing
            text = text[i:]
        return text

if __name__ == "__main__":
    pygame.init()
    game = PolarPizza()
    game.run()