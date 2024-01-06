import pygame
import os
import random
import math
import sys
import neat

# starts game
pygame.init()

# Global Constants
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

BALL = pygame.image.load("Ball.png")

PADDLE = pygame.image.load("Paddle.png")

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Ball:
    def __init__(self):
        self.image = BALL
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = 1
        i = 0
        while i == 0:
            i = random.randint(-9, 9)
        self.velocity = pygame.Vector2(i, 10)

    def update(self, paddle):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        if self.rect.y < 0:
            self.velocity.y = -self.velocity.y

        if paddle.rect.colliderect(self.rect):
            self.velocity.y = -self.velocity.y
            self.velocity *= 1.05
            return True

        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.velocity.x = -self.velocity.x

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))


class Paddle:
    def __init__(self):
        self.image = PADDLE
        self.rect = self.image.get_rect()
        self.speed = 13
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height

    def move(self, index):
        if index == 0:
            self.rect.x += self.speed
        elif index == 1:
            self.rect.x -= self.speed

        if self.rect.x < 0:
            self.rect.x = 0

        if self.rect.x > SCREEN_WIDTH - self.rect.width:
            self.rect.x = SCREEN_WIDTH - self.rect.width

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))


def eval_genomes(genomes, config):
    global points, balls, paddles, ge, nets
    clock = pygame.time.Clock()
    points = 0

    balls = []
    paddles = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        paddles.append(Paddle())
        balls.append(Ball())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score(genomes):
        global points
        points += 1
        if len(genomes) > 0:
            fittest = genomes[0]
            for genome in genomes:
                if genome.fitness > fittest.fitness:
                    fittest = genome
            text = FONT.render(f'Fitness:  {str(fittest.fitness)}', True, (255, 255, 255))
            SCREEN.blit(text, (450, 50))

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((0, 0, 0))

        for i, ball in enumerate(balls):
            collide = ball.update(paddles[i])

            if collide:
                ge[i].fitness += 10

            ball.draw(SCREEN)
            ge[i].fitness += 0.1

            output = nets[i].activate((ball.velocity.x, ball.velocity.y, abs(paddles[i].rect.x - ball.rect.x), abs(paddles[i].rect.y - ball.rect.y)))
            final_output = output.index(max(output)) - 1
            paddles[i].move(final_output)

            if ball.rect.y > SCREEN_HEIGHT:
                ge[i].fitness -= 5
                nets.pop(i)
                ge.pop(i)
                balls.pop(i)
                paddles.pop(i)

        for paddle in paddles:
            paddle.draw(SCREEN)

        if len(balls) == 0:
            run = False
            break

        # ---------Human Player-------#
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        #     paddle.move(True)
        # elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        #     paddle.move(False)
        #
        # if paddle.rect.x < 0:
        #     paddle.rect.x = 0
        #
        # if paddle.rect.x > SCREEN_WIDTH - paddle.rect.width:
        #     paddle.rect.x = SCREEN_WIDTH - paddle.rect.width
        #
        # paddle.draw(SCREEN)

        score(ge)
        clock.tick(30)
        pygame.display.update()



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes)

    print("Best fitness -> {}".format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    run(config_path)

# Inputs:
# 1. Position of ball to paddle on x
# 2. Position of ball to paddle on y
# 3. X-Velocity of ball
# 4. Y-Velocity of ball

# Outputs:
# 1. Move left
# 2. Don't move
# 3. Move right

# Fitness Function
# Reward is based on how long the player can go without letting the ball touch the ground
# -5 if it misses the ball, +10 for if it hits the ball, +1 for each frame it goes without letting the ball hit the ground
