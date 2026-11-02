from __future__ import annotations

import pygame

from src.model import GameMode, PongModel
from src.view import PongView


class PongGame:
    # The controller owns the main game loop and coordinates user input with the model.
    def __init__(self) -> None:
        # Initialize pygame, create the window, and set up the game objects.
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.model = PongModel(self.screen.get_width(), self.screen.get_height())
        self.view = PongView(self.screen)
        self.running = True
        self.menu_visible = True

    def handle_events(self) -> None:
        # Inspect window and keyboard events once per frame.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.model.save_progress()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Escape quits from the menu or returns to the menu during play.
                    if self.menu_visible:
                        self.running = False
                        self.model.save_progress()
                    else:
                        self.model.save_progress()
                        self.menu_visible = True
                elif event.key == pygame.K_1:
                    self.model.set_mode(GameMode.ONE_PLAYER)
                    self.menu_visible = False
                elif event.key == pygame.K_2:
                    self.model.set_mode(GameMode.TWO_PLAYER)
                    self.menu_visible = False
                elif event.key == pygame.K_c:
                    # Press C to cycle through the unlocked paddle colors.
                    self.model.cycle_color()
                    self.model.save_progress()

    def handle_gameplay(self, dt: float) -> None:
        # Do not update world state while the menu is visible.
        if self.menu_visible:
            return

        keys = pygame.key.get_pressed()

        # Player uses W and S to move the left paddle.
        left_direction = 0
        if keys[pygame.K_w]:
            left_direction = -1
        elif keys[pygame.K_s]:
            left_direction = 1
        self.model.left_paddle.move(left_direction, dt)

        # In two-player mode, the right paddle uses the arrow keys.
        if self.model.mode == GameMode.TWO_PLAYER:
            right_direction = 0
            if keys[pygame.K_UP]:
                right_direction = -1
            elif keys[pygame.K_DOWN]:
                right_direction = 1
            self.model.right_paddle.move(right_direction, dt)

        # Advance the game simulation for this frame.
        self.model.update(dt)

    def run(self) -> None:
        # Main loop: process events, update state, then draw the next frame.
        try:
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                self.handle_events()
                if not self.running:
                    break
                self.handle_gameplay(dt)
                self.view.draw(self.model, self.menu_visible)
        finally:
            # The final high score and selected color must be saved even if the game exits
            # while a single-player run is still in progress.
            self.model.save_progress()
            pygame.quit()


if __name__ == "__main__":
    PongGame().run()
