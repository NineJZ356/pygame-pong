from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import random

import pygame


class GameMode(Enum):
    # This enum lists the two available play modes: solo against the CPU or
    # local multiplayer using the same keyboard.
    ONE_PLAYER = "one_player"
    TWO_PLAYER = "two_player"


@dataclass
class Paddle:
    # A paddle is the vertical rectangle that moves up and down to hit the ball.
    x: float
    y: float
    width: int = 18
    height: int = 110
    speed: float = 520.0
    color: tuple[int, int, int] = (255, 255, 255)
    rect: pygame.Rect = field(init=False)

    def __post_init__(self) -> None:
        # Create the rectangle used for drawing and collision checks.
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, dt: float) -> None:
        # direction is -1 for up, 1 for down, and 0 for no movement.
        self.rect.y += direction * self.speed * dt

    def clamp(self, screen_height: int) -> None:
        # Keep the paddle visible on the screen at all times.
        self.rect.y = max(0, min(self.rect.y, screen_height - self.rect.height))

    def update_cpu(self, ball: "Ball", dt: float) -> None:
        # The CPU paddle follows the ball's vertical position with a small delay.
        direction = 0
        if ball.rect.centery > self.rect.centery + 15:
            direction = 1
        elif ball.rect.centery < self.rect.centery - 15:
            direction = -1
        self.move(direction, dt * 0.9)
        self.clamp(ball.screen_height)


@dataclass
class Ball:
    # The ball travels across the field and bounces off walls and paddles.
    x: float
    y: float
    radius: int = 10
    speed: float = 360.0
    color: tuple[int, int, int] = (255, 255, 255)
    screen_width: int = 0
    screen_height: int = 0
    rect: pygame.Rect = field(init=False)
    vx: float = field(init=False)
    vy: float = field(init=False)

    def __post_init__(self) -> None:
        # Build the ball's collision rectangle from its center and radius.
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.reset()

    def reset(self) -> None:
        # Return the ball to the middle and start it moving in a random direction.
        self.rect.center = (self.screen_width / 2, self.screen_height / 2)
        direction = random.choice([-1, 1])
        self.vx = direction * self.speed
        self.vy = random.uniform(-0.9, 0.9) * self.speed

    def update(self, left_paddle: Paddle, right_paddle: Paddle, dt: float) -> tuple[str | None, bool]:
        # Move the ball based on its velocity and the number of seconds in this frame.
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

        # Bounce off the top and bottom walls.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= self.screen_height:
            self.rect.bottom = self.screen_height
            self.vy *= -1

        # Bounce off either paddle and adjust the angle based on impact position.
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self.vx = abs(self.vx) + 15
            self.vy += (self.rect.centery - left_paddle.rect.centery) * 0.12
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self.vx = -abs(self.vx) - 15
            self.vy += (self.rect.centery - right_paddle.rect.centery) * 0.12

        # If the ball exits the left or right side, a point has been scored.
        if self.rect.left <= 0:
            return "right", True
        if self.rect.right >= self.screen_width:
            return "left", True
        return None, False


@dataclass
class Score:
    # Score tracks the point totals for the left and right players.
    left: int = 0
    right: int = 0


@dataclass
class PongModel:
    # The model is the game state manager. It owns the paddles, ball, score, and mode.
    screen_width: int
    screen_height: int
    left_paddle: Paddle = field(init=False)
    right_paddle: Paddle = field(init=False)
    ball: Ball = field(init=False)
    score: Score = field(default_factory=Score)
    mode: GameMode = GameMode.ONE_PLAYER

    def __post_init__(self) -> None:
        # Create the paddle and ball objects once the screen size is known.
        self.left_paddle = Paddle(x=40, y=(self.screen_height - 110) / 2)
        self.right_paddle = Paddle(x=self.screen_width - 58, y=(self.screen_height - 110) / 2)
        self.ball = Ball(
            x=self.screen_width / 2,
            y=self.screen_height / 2,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )

    def reset_round(self) -> None:
        # Put the paddles back in the center and re-serve the ball.
        self.left_paddle.rect.y = (self.screen_height - self.left_paddle.rect.height) / 2
        self.right_paddle.rect.y = (self.screen_height - self.right_paddle.rect.height) / 2
        self.ball.reset()

    def update(self, dt: float) -> None:
        # Keep paddles inside the screen before updating the ball.
        self.left_paddle.clamp(self.screen_height)
        self.right_paddle.clamp(self.screen_height)

        # In one-player mode the right paddle is controlled by the CPU.
        if self.mode == GameMode.ONE_PLAYER:
            self.right_paddle.update_cpu(self.ball, dt)

        # Update ball movement and award a point when a side scores.
        scored, did_score = self.ball.update(self.left_paddle, self.right_paddle, dt)
        if did_score and scored is not None:
            if scored == "left":
                self.score.left += 1
            else:
                self.score.right += 1
            self.ball.reset()

    def set_mode(self, mode: GameMode) -> None:
        # Switch mode and reset the round so a new game starts cleanly.
        self.mode = mode
        self.reset_round()
