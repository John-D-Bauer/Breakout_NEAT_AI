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
        self.velocity = pygame.Vector2(5, 10)

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))


class Paddle:
    def __init__(self):
        self.image = PADDLE
        self.rect = self.image.get_rect()
        self.speed = 13
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - self.rect.height

    def move(self, right):
        if right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))


def main():
    global points
    ball = Ball()
    paddle = Paddle()
    clock = pygame.time.Clock()
    points = 0

    def score():
        global points
        points += 1
        text = FONT.render(f'Points:  {str(points)}', True, (255, 255, 255))
        SCREEN.blit(text, (450, 50))

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((0, 0, 0))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            paddle.move(True)
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            paddle.move(False)

        if paddle.rect.x < 0:
            paddle.rect.x = 0

        if paddle.rect.x > SCREEN_WIDTH - paddle.rect.width:
            paddle.rect.x = SCREEN_WIDTH - paddle.rect.width

        ball.update()
        ball.draw(SCREEN)
        paddle.draw(SCREEN)

        if ball.rect.y > SCREEN_HEIGHT:
            run = False

        if ball.rect.y < 0:
            ball.velocity.y = -ball.velocity.y

        if paddle.rect.colliderect(ball.rect):
            ball.velocity.y = -ball.velocity.y
            ball.velocity *= 1.05

        if ball.rect.x < 0 or ball.rect.x > SCREEN_WIDTH - ball.rect.width:
            ball.velocity.x = -ball.velocity.x

        score()
        clock.tick(30)
        pygame.display.update()

    pygame.quit()
    exit()


if __name__ == "__main__":
    main()
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
