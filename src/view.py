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
        # Draw the background and court layout.
        self.screen.fill((5, 10, 20))

        center_line = pygame.Rect(self.screen.get_width() / 2 - 2, 0, 4, self.screen.get_height())
        pygame.draw.rect(self.screen, (255, 255, 255), center_line)

        # Draw the paddles and ball using the current model state.
        pygame.draw.rect(self.screen, model.left_paddle.color, model.left_paddle.rect)
        pygame.draw.rect(self.screen, model.right_paddle.color, model.right_paddle.rect)
        pygame.draw.circle(self.screen, model.ball.color, model.ball.rect.center, model.ball.radius)

        # Draw the score text in the center top area.
        left_score = self.font.render(str(model.score.left), True, (255, 255, 255))
        right_score = self.font.render(str(model.score.right), True, (255, 255, 255))
        self.screen.blit(left_score, (self.screen.get_width() * 0.35, 24))
        self.screen.blit(right_score, (self.screen.get_width() * 0.60, 24))

        # When the player is in single-player mode, show a compact status panel in the
        # upper-left area without overlapping the main game field.
        if model.mode == model.mode.ONE_PLAYER:
            best_text = self.small_font.render(f"Best: {model.personal_best_seconds:.1f}s", True, (220, 220, 220))
            run_text = self.small_font.render(f"Run: {model.current_survival_seconds:.1f}s", True, (220, 220, 220))
            color_text = self.small_font.render(f"Color: {model.selected_color.title()}", True, (220, 220, 220))
            unlock_text = self.small_font.render(model.next_unlock_label(), True, (220, 220, 220))

            self.screen.blit(best_text, (18, 18))
            self.screen.blit(run_text, (18, 52))
            self.screen.blit(color_text, (18, 86))
            self.screen.blit(unlock_text, (18, 120))

        # Show the main menu before a mode is selected, with a layout that fits the
        # 900x600 viewport and keeps all text on separate lines.
        if menu_visible:
            title = self.font.render("PONG", True, (255, 255, 255))
            prompt = self.small_font.render("Press 1 for single player | 2 for two players", True, (220, 220, 220))
            color_prompt = self.small_font.render("Press C to cycle unlocked paddle colors", True, (220, 220, 220))
            best_text = self.small_font.render(f"Best survival: {model.personal_best_seconds:.1f}s", True, (220, 220, 220))
            unlock_text = self.small_font.render(model.next_unlock_label(), True, (220, 220, 220))
            quit_text = self.small_font.render("Press Esc to quit", True, (220, 220, 220))

            title_x = self.screen.get_width() / 2 - 90
            title_y = 150
            self.screen.blit(title, (title_x, title_y))

            prompt_x = self.screen.get_width() / 2 - 300
            prompt_y = 245
            self.screen.blit(prompt, (prompt_x, prompt_y))
            self.screen.blit(color_prompt, (self.screen.get_width() / 2 - 280, 285))
            self.screen.blit(best_text, (self.screen.get_width() / 2 - 150, 330))
            self.screen.blit(unlock_text, (self.screen.get_width() / 2 - 180, 370))
            self.screen.blit(quit_text, (self.screen.get_width() / 2 - 100, 410))

        # Update the display after all drawing is complete.
        pygame.display.flip()
