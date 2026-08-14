import pygame
from battle_scene import BattleScene

BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220, 0)
GRAY   = (80, 80, 80)

LOCATIONS = [
    {"name": "Forest Outskirts", "x": 200, "y": 300},
    {"name": "Ruined Village",   "x": 500, "y": 200},
    {"name": "Mountain Pass",    "x": 800, "y": 350},
]


class MapScene:
    def __init__(self):
        self.font       = pygame.font.SysFont("monospace", 20)
        self.small_font = pygame.font.SysFont("monospace", 14)
        self.selected   = 0

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(LOCATIONS)
            if event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(LOCATIONS)
            if event.key == pygame.K_RETURN:
                manager.set_scene(BattleScene())

    def update(self, manager):
        pass

    def draw(self, screen):
        screen.fill((10, 20, 40))

        for i, loc in enumerate(LOCATIONS):
            color  = YELLOW if i == self.selected else GRAY
            radius = 16 if i == self.selected else 10
            pygame.draw.circle(screen, color, (loc["x"], loc["y"]), radius)
            label = self.small_font.render(loc["name"], True, color)
            screen.blit(label, (loc["x"] - label.get_width() // 2, loc["y"] + 20))

        selected_name = LOCATIONS[self.selected]["name"]
        title = self.font.render(f"> {selected_name}", True, WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 680))

        hint = self.small_font.render("LEFT / RIGHT to select   ENTER to go", True, GRAY)
        screen.blit(hint, (screen.get_width() // 2 - hint.get_width() // 2, 740))