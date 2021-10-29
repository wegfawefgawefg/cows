import pygame
import random

WIDTH = 1920 - 200
HEIGHT = 1080 - 200

W = 10
H = 10

def drift_color(color):
    drift_amount = 26
    dr = random.randint(-drift_amount, drift_amount)
    dg = random.randint(-drift_amount, drift_amount)
    db = random.randint(-drift_amount, drift_amount)
    return (color[0] + dr, color[1] + dg, color[2] + db)

def bound_color(color):
    return (max(0, min(255, color[0])), max(0, min(255, color[1])), max(0, min(255, color[2])))

class Grass:
    def draw(self, screen, x, y, x_scale, y_scale):
        pygame.draw.rect(screen, (0, 170, 50),(x,y, x_scale, y_scale))

    def step(self, grass_grid, x, y):
        if random.random() < 0.01:
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            new_x, new_y = x + dx, y + dy
            # bounds check
            new_x = max(0, min(new_x, len(grass_grid[0]) - 1))
            new_y = max(0, min(new_y, len(grass_grid) - 1))
            taken = grass_grid[new_y][new_x]
            if not taken:
                grass_grid[new_y][new_x] = self
class Cow:
    STARTING_HUNGER = 60 * 2
    def __init__(self, color):
        self.hunger = Cow.STARTING_HUNGER
        self.alive = True
        self.age = 0
        self.time_since_spawned = 0
        self.dead_for = 0
        self.color = drift_color(color)
        self.color = bound_color(self.color)

    def draw(self, screen, x, y, x_scale, y_scale):
        color = self.color
        if self.hunger < Cow.STARTING_HUNGER // 2:
            #pygame.draw.circle(screen, (255, 0, 0), (x+W, y+H), W//2+2)
            pygame.draw.rect(screen, (255, 0, 0), (x-4, y-4, x_scale+8, y_scale+8))
        if not self.alive:
            # make cow more grey
            color = (color[0] // 2, color[1] // 2, color[2] // 2)
            color = bound_color(color)
        #pygame.draw.circle(screen, color, (x+W, y+H), W//2)
        pygame.draw.rect(screen, color, (x, y, x_scale, y_scale))

    def step(self, field, x, y):
        self.age += 1
        self.hunger -= 1
        self.time_since_spawned += 1

        if self.alive:
            if self.hunger <= 0:
                self.alive = False
            self.eat(field.grass, x, y)
            self.move(field.cows, x, y)
            self.split(field.cows, x, y)
        else:
            self.dead_for += 1
            if self.dead_for > 50:
                field.cows[y][x] = None
                #field.grass[y][x] = Grass()
                ## spawn grass in nearby cells
                #for i in range(-1, 2):
                #    for j in range(-1, 2):
                #        if (i, j) != (0, 0):
                #            if 0 <= x + i < len(field.grass[0]) and 0 <= y + j < len(field.grass):
                #                field.grass[y + j][x + i] = Grass()
        
        self.hunger = min(self.hunger, Cow.STARTING_HUNGER * 2)

    def eat(self, grass_grid, x, y):
        grass = grass_grid[y][x]
        if grass:
            grass_grid[y][x] = None
            self.hunger += 10

    def move(self, cow_grid, x, y):
        if any([
            (self.hunger < Cow.STARTING_HUNGER // 2) and random.random() < 0.5,
            random.random() < 0.1
        ]):
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            new_x, new_y = x + dx, y + dy
            # bounds check
            new_x = max(0, min(new_x, len(cow_grid[0]) - 1))
            new_y = max(0, min(new_y, len(cow_grid) - 1))
            taken = cow_grid[new_y][new_x]
            if not taken:
                cow_grid[y][x] = None
                cow_grid[new_y][new_x] = self

    def split(self, cow_grid, x, y):
        if all([
            #self.hunger > (Cow.STARTING_HUNGER // 2),
            self.time_since_spawned > (60 * 2),
            self.age > (60 * 20)
        ]):
            dx = random.randint(-1, 1)
            dy = random.randint(-1, 1)
            new_x, new_y = x + dx, y + dy
            # bounds check
            new_x = max(0, min(new_x, len(cow_grid[0]) - 1))
            new_y = max(0, min(new_y, len(cow_grid) - 1))
            taken = cow_grid[new_y][new_x]
            if not taken:
                cow_grid[new_y][new_x] = Cow(color=self.color)
                self.time_since_spawned = 0

class GrassyField:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.x_scale = WIDTH // self.width
        self.y_scale = HEIGHT // self.height    

        self.cows = [[None for x in range(width)] for y in range(height)]
        self.grass = [[None for x in range(width)] for y in range(height)]

        self.draw_cows = True

        # add 20 cows
        for _ in range(50):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.cows[y][x] = Cow(color=(255, 255, 255))
        
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:
                    self.grass[y][x] = Grass()

        for _ in range(10):
            self.grass[random.randint(0, self.height - 1)][random.randint(0, self.width - 1)] = Grass()

    def toggle_draw_cows(self):
        self.draw_cows = not self.draw_cows

    def step(self):
        for x in range(self.width):
            for y in range(self.height):
                grass = self.grass[y][x]
                if grass:
                    grass.step(self.grass, x, y)

                cow = self.cows[y][x]
                if cow:
                    cow.step(self, x, y)
                

    def draw(self, surface):
        #for x in range(self.width):
        #    for y in range(self.height):
        #        pygame.draw.rect(surface, (255, 255, 255), (
        #                x * self.x_scale, 
        #                y * self.y_scale, 
        #                self.x_scale, 
        #                self.y_scale), 
        #            1)

        for x in range(self.width):
            for y in range(self.height):
                grass = self.grass[y][x]
                if grass:
                    grass.draw(surface, x *  self.x_scale, y * self.y_scale, self.x_scale, self.y_scale)


        if self.draw_cows:
            for x in range(self.width):
                for y in range(self.height):
                    cow = self.cows[y][x]
                    if cow:
                        cow.draw(surface, x *  self.x_scale, y * self.y_scale, self.x_scale, self.y_scale)

pygame.init()


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    ratio = 18
    gf = GrassyField(16* ratio, 9* ratio)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            # on press c
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                gf.toggle_draw_cows()
        screen.fill((0, 0, 0))
        gf.step()
        gf.draw(screen)
        pygame.display.flip()
        clock.tick(1000)

main()