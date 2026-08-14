import pygame

class Menu:

    def __init__(self, options: list, on_confirm, on_cancel=None):
        self.options = options
        self.selected = 0
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    def handle_key(self, key):
        if not self.options:
            return
        if key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(self.options)
        if key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(self.options)
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        if key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        number_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
        for i, k in enumerate(number_keys):
            if key == k and i < len(self.options):
                self.selected = i
        if key == pygame.K_RETURN:
            self.on_confirm(self.options[self.selected])
        if key == pygame.K_ESCAPE and self.on_cancel:
            self.on_cancel()

    @property
    def current(self):
        return self.options[self.selected] if self.options else None