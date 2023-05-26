import pygame
import sys
from random import randint, choice
from math import sin, cos, radians
import time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30


class Game:
    def __init__(self):
        pygame.init()
        screen_info = pygame.display.Info()
        self.screen = pygame.display.set_mode(
            (screen_info.current_w, screen_info.current_h),
            pygame.FULLSCREEN
        )
        self.rect = self.screen.get_rect()
        self.player_1 = Paddle(
            screen_rect=self.rect,
            center=(self.rect.width * 0.1, self.rect.centery),
            size=(self.rect.width * 0.01, self.rect.height * 0.1),
            keys=(pygame.K_w, pygame.K_s),
        )
        self.player_2 = Paddle(
            screen_rect=self.rect,
            center=(self.rect.width * 0.9, self.rect.centery),
            size=(self.rect.width * 0.01, self.rect.height * 0.1),
            is_automatic=True,
            delay=100
           

        )
        self.ball = ball(
            self.rect,
            self.rect.center,
            (self.rect.width * 0.01, self.rect.width * 0.01)
        )
        self.score_1 = Score(
            center=(self.rect.width * 0.25, self.rect.height * 0.10),
            paddle=self.player_1
        )
        self.score_2 = Score(
            center=(self.rect.width * 0.75, self.rect.height * 0.10),
            paddle=self.player_2
        )
            
        self.paddles = pygame.sprite.Group()
        self.balls = pygame.sprite.Group()
        self.scores = pygame.sprite.Group()
        self.paddles.add(self.player_1)
        self.paddles.add(self.player_2)
        self.ball.throw_in()
        self.balls.add(self.ball)
        self.scores.add(self.score_1)
        self.scores.add(self.score_2)
        self.clock = pygame.time.Clock()
        self.main_loop()



    def check_goal(self):
        if self.ball.rect.right >= self.rect.right:
            self.player_1.score += 1
            print("гол правому")
            self.ball.throw_in()
        if self.ball.rect.left <= self.rect.left:
            self.player_2.score += 1
            self.ball.throw_in()
            print("гол левому")
    
        
    

    def main_loop(self):
        game = True
        while game:            
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                game = False

            self.screen.fill(BLACK)
            self.paddles.update(self.ball, dt)
            self.scores.update()
            self.check_goal()
            self.paddles.draw(self.screen)
            self.balls.update(self.paddles)
            self.balls.draw(self.screen)
            self.scores.draw(self.screen)
            pygame.draw.line(
                self.screen,
                WHITE,
                (self.rect.centerx, self.rect.bottom),
                (self.rect.centerx, self.rect.top)
            )
            pygame.display.flip()

        pygame.quit()


class Paddle(pygame.sprite.Sprite):
    def __init__(
            self,
            screen_rect=None,
            center=(0, 0),
            size=(10, 100),
            color=WHITE,
            keys=(pygame.K_UP, pygame.K_DOWN),
            is_automatic=False,
            speed=10,
            score=0,
            delay=150

            
    ):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.keys = keys
        self.is_automatic = is_automatic
        self.speed = speed
        self.screen_rect = screen_rect
        self.score = score
        self.elapsed_time = 0
        self.delay = delay
        self.direction = 0
        

    def update(self, ball, dt):
        keys = pygame.key.get_pressed()        
        self.prev_y = self.rect.centery
        if not self.is_automatic:
            if keys[self.keys[0]]:
                if self.rect.top >= self.screen_rect.top:
                    self.rect.y -= self.speed
            if keys[self.keys[1]]:
                if self.rect.bottom <= self.screen_rect.bottom:
                    self.rect.y += self.speed

        else:
            self.elapsed_time += dt
            if self.elapsed_time >= self.delay:
                if ball.rect.centery < self.rect.centery:
                    if self.rect.top >= self.screen_rect.top:
                        self.rect.y -= self.speed
                if ball.rect.centery > self.rect.centery:
                    if self.rect.bottom <= self.screen_rect.bottom:
                        self.rect.y += self.speed
                self.elapsed_time = 0

        if self.rect.centery < self.prev_y:
            self.direction = 0 
        elif self.rect.centery > self.prev_y:
            self.direction = 180
        else:
            self.direction = 90
        




class ball(pygame.sprite.Sprite):
    """ мяч """
    def __init__(
            self,
            screen_rect=None,
            center=(0, 0),
            size=(10, 10),
            color=WHITE,
            speed=10,
            velocity_x=None,
            velocity_y=None,
            direction=90
    ) -> None:
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.direction = direction
        self.speed = speed
        self.screen_rect = screen_rect

    def update(self, paddles):
        self.move()
        self.bounce_walls()
        self.bounce_paddles(paddles)
        


    def move(self):
        self.velocity_x = sin(radians(self.direction)) * self.speed
        self.velocity_y = cos(radians(self.direction)) * self.speed * -1
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y    

    def bounce_walls(self):
        """
        отскок мяч от верхней и нижней границы:
        """
        if self.rect.top <= self.screen_rect.top:
            self.direction *= -1
            self.direction += 180
        if self.rect.bottom >= self.screen_rect.bottom:
            self.direction *= -1
            self.direction += 180    

    def bounce_paddles(self, paddles):
        for paddle in paddles:
            if paddle.rect.colliderect(self.rect):
                self.direction *= -1
                if paddle.direction == 0:
                    self.direction += 10
                elif paddle.direction == 0:  
                    self.direction -= 10

    def throw_in(self):
        """
        центрирует мяч и запускает 
        """
        self.rect.center = self.screen_rect.center
        self.direction = choice((randint(45, 135), randint(225, 315)))    


    

class Score(pygame.sprite.Sprite):
    def __init__(
            self, 
            color=WHITE, 
            size=70, 
            center=(0, 0), 
            paddle=None
    ):
        
        super().__init__()
        self.paddle = paddle
        self.color = color
        self.center = center
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render(str(paddle.score), True, color)
        self.rect = self.image.get_rect(center=center)
    def update(self):
        self.image = self.font.render(str(self.paddle.score), True, self.color)
        self.rect = self.image.get_rect(center=self.center)

game = Game()
sys.exit()
