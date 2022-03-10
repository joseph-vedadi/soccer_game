from enum import Enum
import random
import pygame
import pymunk

pygame.init()
DIMENSION_X, DIMENSION_Y = 800, 1100
PLAYER_DIMENSION = 80
GOAL_DIMENSION = 300
BALL_RADIUS = 20
BALL_VELOCITY = 1000
display = pygame.display.set_mode((DIMENSION_X, DIMENSION_Y))
clock = pygame.time.Clock()
space = pymunk.Space()
FPS = 90
FLOOR_COLOR = pygame.Color("#94e689")
US_GOAL_COLOR = pygame.Color("#1207e6")
ENEMY_GOAL_COLOR = pygame.Color("#a83632")
US_PLAYER_COLOR = pygame.Color("#1207e6")
ENEMY_PLAYER_COLOR = pygame.Color("#a83632")
WALL_COLOR = pygame.Color("#a8a8a8")
BALL_COLOR = pygame.Color("#FFFFFF")


class TeamType(Enum):
    US = 10
    ENEMY = 20


class Player:
    def __init__(self, position, team: TeamType) -> None:
        self.team = team
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.shape = pymunk.Poly.create_box(self.body, (PLAYER_DIMENSION, PLAYER_DIMENSION), PLAYER_DIMENSION)
        self.shape.density = 1
        self.shape.elasticity = 1
        self.shape.collision_type = 2
        space.add(self.body, self.shape)

    def draw(self) -> None:
        x, y = self.body.position
        pygame.draw.rect(display, BALL_COLOR, (x, y, PLAYER_DIMENSION, PLAYER_DIMENSION), PLAYER_DIMENSION)

    @property
    def color(self):
        if self.team == TeamType.US:
            return US_PLAYER_COLOR
        else:
            return ENEMY_PLAYER_COLOR


class Ball:
    def __init__(self, position) -> None:
        self.body = pymunk.Body(mass=0.5)
        self.position = position
        self.shape = pymunk.Circle(self.body, BALL_RADIUS)
        self.shape.density = 1
        self.shape.elasticity = 1
        self.shape.collision_type = 2
        space.add(self.body, self.shape)
        self.reset()

    @staticmethod
    def get_random_velocity() -> float:
        return random.uniform(BALL_VELOCITY * 2 / 3, BALL_VELOCITY) * random.choice([1, -1])

    def reset(self):
        self.body.position = self.position
        self.body.velocity = Ball.get_random_velocity(), Ball.get_random_velocity()

    def draw(self) -> None:
        pygame.draw.circle(display, BALL_COLOR, self.body.position, BALL_RADIUS)


class Wall:
    def __init__(self, p1, p2) -> None:
        self.p1, self.p2 = p1, p2
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, p1, p2, self.width)
        self.shape.elasticity = 0.7
        space.add(self.body, self.shape)

    @property
    def width(self) -> int:
        return 20

    @property
    def color(self):
        return WALL_COLOR

    def draw(self) -> None:
        pygame.draw.line(display, self.color, self.p1, self.p2, self.width)


class Goal(Wall):
    def __init__(self, p1, p2, team: TeamType = TeamType.US) -> None:
        self.team = team
        self.current_score = 0
        super().__init__(p1, p2)
        self.shape.collision_type = self.team.value

    @property
    def width(self):
        return 50

    @property
    def score(self) -> float:
        return self.current_score

    def add_score(self) -> None:
        self.current_score += 1

    @property
    def color(self):
        if self.team == TeamType.US:
            return US_GOAL_COLOR
        else:
            return ENEMY_GOAL_COLOR


def print_score(us: Goal, enemy: Goal):
    text = pygame.font.SysFont("comicsansms", 25).render(f"Score : {us.score} Vs. {enemy.score}", True, (0, 0, 0))
    display.blit(text, (0, 0))


def continue_paying() -> bool:
    for even in pygame.event.get():
        if even.type == pygame.QUIT:
            return False
    return True


def game():
    drawables = []
    walls = [
        Wall((0, 0), (0, DIMENSION_Y)),
        Wall((0, 0), (DIMENSION_X, 0)),
        Wall((0, DIMENSION_Y), (DIMENSION_X, DIMENSION_Y)),
        Wall((DIMENSION_X, 0), (DIMENSION_X, DIMENSION_Y)),
    ]
    drawables += walls
    # Goals
    enemy, us = (
        Goal(((DIMENSION_X - GOAL_DIMENSION) / 2, 0), ((DIMENSION_X - (DIMENSION_X - GOAL_DIMENSION) / 2), 0), team=TeamType.ENEMY),
        Goal(
            ((DIMENSION_X - GOAL_DIMENSION) / 2, DIMENSION_Y),
            ((DIMENSION_X - (DIMENSION_X - GOAL_DIMENSION) / 2), DIMENSION_Y),
            team=TeamType.US,
        ),
    )
    ball = Ball((DIMENSION_X / 2, DIMENSION_Y / 2))
    drawables += [enemy, us, ball]
    us_player = Player((DIMENSION_X / 2, DIMENSION_Y - GOAL_DIMENSION - PLAYER_DIMENSION), team=TeamType.US)
    drawables.append(us_player)

    def us_collide(att, space, data):
        enemy.add_score()
        # ball.reset()

    def enemy_collide(att, space, data):
        us.add_score()
        # ball.reset()

    space.add_collision_handler(us.shape.collision_type, ball.shape.collision_type).separate = us_collide
    space.add_collision_handler(enemy.shape.collision_type, ball.shape.collision_type).separate = enemy_collide

    while continue_paying():
        display.fill(FLOOR_COLOR)
        pygame.draw.line(
            display,
            WALL_COLOR,
            (0, DIMENSION_Y / 2),
            (DIMENSION_X, DIMENSION_Y / 2),
            2,
        )
        pygame.draw.circle(display, WALL_COLOR, (DIMENSION_X / 2, DIMENSION_Y / 2), DIMENSION_X / 6, 2)
        [obj.draw() for obj in drawables]
        print_score(us, enemy)
        pygame.display.update()
        clock.tick(10000)
        space.step(1 / FPS)


game()
pygame.quit()
