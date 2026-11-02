from __future__ import annotations

import pygame

from src.model import PongModel


class PongView:
    # The view is responsible for rendering every visible component of the game.
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 84)
        self.small_font = pygame.font.Font(None, 42)

    def draw(self, model: PongModel, menu_visible: bool) -> None:
        # Draw the game field while a mode is active.
        self.screen.fill((5, 10, 20))

        if menu_visible:
            # The menu is rendered on a solid dark background so the court does not
            # show through behind the text, and no in-game HUD is duplicated here.
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 240))
            self.screen.blit(overlay, (0, 0))

            title = self.font.render("PONG", True, (255, 255, 255))
            title_rect = title.get_rect(center=(self.screen.get_width() / 2, 120))
            self.screen.blit(title, title_rect)

            menu_lines = [
                "Press 1 for single player   |   Press 2 for two players",
                "Left: W / S   |   Right: Up / Down",
                "C: cycle paddle colors   |   Esc: quit",
                f"Selected color: {model.selected_color.title()}",
            ]

            y = 220
            for line in menu_lines:
                surface = self.small_font.render(line, True, (220, 220, 220))
                rect = surface.get_rect(center=(self.screen.get_width() / 2, y))
                self.screen.blit(surface, rect)
                y += 40

            pygame.display.flip()
            return

        # Draw the court and game elements during play.
        center_line = pygame.Rect(self.screen.get_width() / 2 - 2, 0, 4, self.screen.get_height())
        pygame.draw.rect(self.screen, (255, 255, 255), center_line)

        pygame.draw.rect(self.screen, model.left_paddle.color, model.left_paddle.rect)
        pygame.draw.rect(self.screen, model.right_paddle.color, model.right_paddle.rect)
        pygame.draw.circle(self.screen, model.ball.color, model.ball.rect.center, model.ball.radius)

        # Render the score text in the center top area.
        left_score = self.font.render(str(model.score.left), True, (255, 255, 255))
        right_score = self.font.render(str(model.score.right), True, (255, 255, 255))
        self.screen.blit(left_score, (self.screen.get_width() * 0.35, 24))
        self.screen.blit(right_score, (self.screen.get_width() * 0.60, 24))

        # During single-player mode, show the compact survival HUD in the upper-left.
        if model.mode == model.mode.ONE_PLAYER:
            best_text = self.small_font.render(f"Best: {model.personal_best_seconds:.1f}s", True, (220, 220, 220))
            run_text = self.small_font.render(f"Run: {model.current_survival_seconds:.1f}s", True, (220, 220, 220))
            color_text = self.small_font.render(f"Color: {model.selected_color.title()}", True, (220, 220, 220))
            unlock_text = self.small_font.render(model.next_unlock_label(), True, (220, 220, 220))

            self.screen.blit(best_text, (18, 18))
            self.screen.blit(run_text, (18, 52))
            self.screen.blit(color_text, (18, 86))
            self.screen.blit(unlock_text, (18, 120))

        # Update the display after all drawing is complete.
        pygame.display.flip()
