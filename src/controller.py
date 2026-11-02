from __future__ import annotations

import pygame

from src.model import GameMode, PongModel
from src.view import PongView


class PongGame:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.model = PongModel(self.screen.get_width(), self.screen.get_height())
        self.view = PongView(self.screen)
        self.running = True
        self.menu_visible = True

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.menu_visible:
                        self.running = False
                    else:
                        self.menu_visible = True
                elif event.key == pygame.K_1:
                    self.model.set_mode(GameMode.ONE_PLAYER)
                    self.menu_visible = False
                elif event.key == pygame.K_2:
                    self.model.set_mode(GameMode.TWO_PLAYER)
                    self.menu_visible = False

    def handle_gameplay(self, dt: float) -> None:
        if self.menu_visible:
            return

        keys = pygame.key.get_pressed()

        left_direction = 0
        if keys[pygame.K_w]:
            left_direction = -1
        elif keys[pygame.K_s]:
            left_direction = 1
        self.model.left_paddle.move(left_direction, dt)

        if self.model.mode == GameMode.TWO_PLAYER:
            right_direction = 0
            if keys[pygame.K_UP]:
                right_direction = -1
            elif keys[pygame.K_DOWN]:
                right_direction = 1
            self.model.right_paddle.move(right_direction, dt)

        self.model.update(dt)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.handle_gameplay(dt)
            self.view.draw(self.model, self.menu_visible)

        pygame.quit()


if __name__ == "__main__":
    PongGame().run()
