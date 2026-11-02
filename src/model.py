from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import random
from pathlib import Path

import pygame


class GameMode(Enum):
    # This enum represents the two game modes the player can select.
    ONE_PLAYER = "one_player"
    TWO_PLAYER = "two_player"


# Player paddle colors available for selection. The classic color is always
# unlocked, while the others are earned by surviving longer in one-player mode.
PADDLE_COLORS: dict[str, tuple[int, int, int]] = {
    "classic": (255, 255, 255),
    "red": (255, 97, 97),
    "blue": (102, 180, 255),
    "green": (113, 255, 160),
}

# Survival time thresholds for unlocking each paddle skin.
PADDLE_COLOR_UNLOCKS: dict[str, float] = {
    "classic": 0.0,
    "red": 5.0,
    "blue": 12.0,
    "green": 20.0,
}


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
        # This rectangle is used for both drawing and collision detection.
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, direction: int, dt: float) -> None:
        # direction is -1 for up, 1 for down, and 0 for no movement.
        self.rect.y += direction * self.speed * dt

    def clamp(self, screen_height: int) -> None:
        # Keep the paddle visible within the game window.
        self.rect.y = max(0, min(self.rect.y, screen_height - self.rect.height))

    def update_cpu(self, ball: "Ball", dt: float) -> None:
        # The CPU paddle tries to match the ball's vertical position with a small
        # tracking delay to make the opponent feel more natural.
        direction = 0
        if ball.rect.centery > self.rect.centery + 15:
            direction = 1
        elif ball.rect.centery < self.rect.centery - 15:
            direction = -1
        self.move(direction, dt * 0.9)
        self.clamp(ball.screen_height)


@dataclass
class Ball:
    # The ball travels across the court and rebounds off walls and paddles.
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
        # Create the ball's collision rectangle and launch it into motion.
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.reset()

    def reset(self) -> None:
        # Center the ball and start it moving in a random direction.
        self.rect.center = (self.screen_width / 2, self.screen_height / 2)
        direction = random.choice([-1, 1])
        self.vx = direction * self.speed
        self.vy = random.uniform(-0.9, 0.9) * self.speed

    def update(self, left_paddle: Paddle, right_paddle: Paddle, dt: float) -> tuple[str | None, bool]:
        # Move the ball based on velocity and the amount of time elapsed in this frame.
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

        # Bounce off the top and bottom walls.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy *= -1
        elif self.rect.bottom >= self.screen_height:
            self.rect.bottom = self.screen_height
            self.vy *= -1

        # Bounce off either paddle and adjust the angle by impact position.
        if self.rect.colliderect(left_paddle.rect):
            self.rect.left = left_paddle.rect.right
            self.vx = abs(self.vx) + 15
            self.vy += (self.rect.centery - left_paddle.rect.centery) * 0.12
        elif self.rect.colliderect(right_paddle.rect):
            self.rect.right = right_paddle.rect.left
            self.vx = -abs(self.vx) - 15
            self.vy += (self.rect.centery - right_paddle.rect.centery) * 0.12

        # If the ball crosses either side, that player scores a point.
        if self.rect.left <= 0:
            return "right", True
        if self.rect.right >= self.screen_width:
            return "left", True
        return None, False


@dataclass
class Score:
    # Tracks the point totals for each side.
    left: int = 0
    right: int = 0


@dataclass
class PongModel:
    # The model stores the state of the game, including the survival timer and
    # unlocked paddle upgrade information for one-player mode.
    screen_width: int
    screen_height: int
    left_paddle: Paddle = field(init=False)
    right_paddle: Paddle = field(init=False)
    ball: Ball = field(init=False)
    score: Score = field(default_factory=Score)
    mode: GameMode = GameMode.ONE_PLAYER
    selected_color: str = "classic"
    unlocked_colors: set[str] = field(default_factory=lambda: {"classic"})
    personal_best_seconds: float = 0.0
    current_survival_seconds: float = 0.0
    progress_file: Path | None = field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "pong_progress.json"
    )

    def __post_init__(self) -> None:
        # Create the paddles and ball once the screen dimensions are known.
        self.left_paddle = Paddle(x=40, y=(self.screen_height - 110) / 2)
        self.right_paddle = Paddle(x=self.screen_width - 58, y=(self.screen_height - 110) / 2)
        self.ball = Ball(
            x=self.screen_width / 2,
            y=self.screen_height / 2,
            screen_width=self.screen_width,
            screen_height=self.screen_height,
        )
        self.load_progress()
        self._apply_selected_color()

    def _apply_selected_color(self) -> None:
        # Use the selected color for the player's paddle while leaving the CPU
        # paddle in the default white style.
        if self.selected_color not in PADDLE_COLORS:
            self.selected_color = "classic"
        self.left_paddle.color = PADDLE_COLORS[self.selected_color]
        self.right_paddle.color = (255, 255, 255)

    def load_progress(self) -> None:
        # Load the saved best survival time and unlocked colors from disk.
        if self.progress_file is None or not self.progress_file.exists():
            return

        try:
            data = json.loads(self.progress_file.read_text())
        except (OSError, ValueError):
            return

        self.personal_best_seconds = float(data.get("personal_best_seconds", 0.0))
        self.selected_color = str(data.get("selected_color", self.selected_color))
        unlocked = data.get("unlocked_colors", ["classic"])
        self.unlocked_colors = {str(item) for item in unlocked}

        if not self.unlocked_colors:
            self.unlocked_colors = {"classic"}
        if self.selected_color not in self.unlocked_colors:
            self.selected_color = "classic"

        self._unlock_colors_for_score()

    def save_progress(self) -> None:
        # Persist the best survival time, selected color, and unlocked colors.
        if self.progress_file is None:
            return

        payload = {
            "personal_best_seconds": round(self.personal_best_seconds, 2),
            "selected_color": self.selected_color,
            "unlocked_colors": sorted(self.unlocked_colors),
        }
        self.progress_file.write_text(json.dumps(payload, indent=2))

    def _unlock_colors_for_score(self) -> None:
        # Any color whose threshold is met becomes available for selection.
        unlocked = set(self.unlocked_colors)
        for color_name, threshold in PADDLE_COLOR_UNLOCKS.items():
            if self.personal_best_seconds >= threshold:
                unlocked.add(color_name)
        self.unlocked_colors = unlocked

        if self.selected_color not in self.unlocked_colors:
            self.selected_color = "classic"

    def cycle_color(self) -> None:
        # Move to the next unlocked paddle color in a circular order.
        order = ["classic", "red", "blue", "green"]
        current_index = order.index(self.selected_color)

        for offset in range(1, len(order) + 1):
            next_color = order[(current_index + offset) % len(order)]
            if next_color in self.unlocked_colors:
                self.selected_color = next_color
                self._apply_selected_color()
                self.save_progress()
                return

    def next_unlock_label(self) -> str:
        # Displays the next paddle skin the player can unlock.
        for color_name, threshold in PADDLE_COLOR_UNLOCKS.items():
            if color_name not in self.unlocked_colors:
                return f"Next unlock: {color_name.title()} at {threshold:.0f}s"
        return "All paddle colors unlocked"

    def reset_round(self) -> None:
        # Reset the court to the center and serve the ball again.
        self.left_paddle.rect.y = (self.screen_height - self.left_paddle.rect.height) / 2
        self.right_paddle.rect.y = (self.screen_height - self.right_paddle.rect.height) / 2
        self.ball.reset()

    def update(self, dt: float) -> None:
        # Keep paddles inside the screen bounds before processing the ball.
        self.left_paddle.clamp(self.screen_height)
        self.right_paddle.clamp(self.screen_height)

        if self.mode == GameMode.ONE_PLAYER:
            # In one-player mode, the timer counts the seconds survived while the
            # human player has not yet conceded a point.
            self.current_survival_seconds += dt
            self.personal_best_seconds = max(self.personal_best_seconds, self.current_survival_seconds)
            self._unlock_colors_for_score()
            self.right_paddle.update_cpu(self.ball, dt)

        scored, did_score = self.ball.update(self.left_paddle, self.right_paddle, dt)
        if did_score and scored is not None:
            if scored == "left":
                self.score.left += 1
            elif scored == "right":
                # A concession ends the survival run for the human player.
                if self.mode == GameMode.ONE_PLAYER:
                    self.personal_best_seconds = max(self.personal_best_seconds, self.current_survival_seconds)
                    self._unlock_colors_for_score()
                    self.current_survival_seconds = 0.0
                    self.save_progress()
                self.score.right += 1
            self.ball.reset()

    def set_mode(self, mode: GameMode) -> None:
        # Switch the game mode and reset the round so the next mode starts cleanly.
        self.mode = mode
        self._apply_selected_color()
        if self.mode == GameMode.ONE_PLAYER:
            self.current_survival_seconds = 0.0
        self.reset_round()

