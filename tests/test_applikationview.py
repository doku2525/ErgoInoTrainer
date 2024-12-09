from unittest import TestCase
import time

import pygame


class test_PygameApplikationview(TestCase):

    # def setUp(self):
    #     pygame.init()
    #     self.screen = pygame.display.set_mode((760, 455))
    #     #self.screen = pygame.Surface((760, 455))
    #
    # def test_draw_intervall_element(self):
    #     for fontname in pygame.font.get_fonts():
    #         ffont = pygame.font.SysFont(fontname, 30)
    #         font = pygame.font.SysFont(fontname, 200)
    #         for zahl in range(1, 150, 10):
    #             self.screen.fill((255, 255, 255))
    #             ftext = ffont.render(f"{fontname}", True, (0, 255, 0))
    #             ftext_rect = ftext.get_rect()
    #             ftext_rect.topleft = (20, 10)
    #             self.screen.blit(ftext, ftext_rect.topleft)
    #             text = font.render(f"{zahl:3d}", True, (0, 255, 0))
    #             text_rect = text.get_rect()
    #             text_rect.topleft = (122, 46)
    #             expected_rect = pygame.Rect(122, 46, 363, 218)
    #             pygame.draw.rect(self.screen, (0, 0, 0), expected_rect, 1)
    #             self.screen.blit(text, text_rect.topleft)
    #             pygame.display.flip()
    #             time.sleep(0.2)
    #             #self.assertEqual((482, 246), text_rect.bottomright, f"Zahl = {zahl}")
    #
    #     pygame.quit()

    def test_draw_daten(self):
        pass

    def test_draw_element(self):
        pass

    def test_draw_element_with_rect(self):
        pass

    def test_build_elements(self):
        pass
