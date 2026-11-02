from __future__ import annotations

import pygame

from src.model import PongModel


class PongView:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 84)
        self.small_font = pygame.font.Font(None, 42)

    def draw(self, model: PongModel, menu_visible: bool) -> None:
        self.screen.fill((5, 10, 20))

        center_line = pygame.Rect(self.screen.get_width() / 2 - 2, 0, 4, self.screen.get_height())
        pygame.draw.rect(self.screen, (255, 255, 255), center_line)

        pygame.draw.rect(self.screen, model.left_paddle.color, model.left_paddle.rect)
        pygame.draw.rect(self.screen, model.right_paddle.color, model.right_paddle.rect)
        pygame.draw.circle(self.screen, model.ball.color, model.ball.rect.center, model.ball.radius)

        left_score = self.font.render(str(model.score.left), True, (255, 255, 255))
        right_score = self.font.render(str(model.score.right), True, (255, 255, 255))
        self.screen.blit(left_score, (self.screen.get_width() * 0.35, 24))
        self.screen.blit(right_score, (self.screen.get_width() * 0.60, 24))

        if menu_visible:
            title = self.font.render("PONG", True, (255, 255, 255))
            prompt = self.small_font.render("Press 1 for single player | 2 for two players", True, (220, 220, 220))
            subtitle = self.small_font.render("Press Esc to quit", True, (220, 220, 220))
            self.screen.blit(title, (self.screen.get_width() / 2 - 90, 180))
            self.screen.blit(prompt, (self.screen.get_width() / 2 - 300, 290))
            self.screen.blit(subtitle, (self.screen.get_width() / 2 - 100, 340))

        pygame.display.flip()
