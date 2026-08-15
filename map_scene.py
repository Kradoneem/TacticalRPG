import pygame
from battle_scene import BattleScene
from menu import Menu
from unit import Unit

LOCATION_ENEMIES = {
    "Forest Outskirts": lambda: [
        Unit("Goblin", level=1, hp=20, mp=0,  attack=8,  defense=2, speed=5, wisdom=2),
        Unit("Orc",    level=2, hp=35, mp=0,  attack=10, defense=4, speed=3, wisdom=1),
    ],
    "Ruined Village": lambda: [
        Unit("Bandit",    level=2, hp=25, mp=0,  attack=10, defense=3, speed=6, wisdom=1),
        Unit("Dark Mage", level=2, hp=18, mp=20, attack=14, defense=1, speed=7, wisdom=8),
    ],
    "Mountain Pass": lambda: [
        Unit("Stone Troll", level=3, hp=50, mp=0, attack=12, defense=6, speed=2, wisdom=1),
    ],
}

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GRAY   = (80,  80,  80)
DIM    = (40,  40,  40)

LOCATIONS = [
    {"name": "Forest Outskirts", "x": 200, "y": 300},
    {"name": "Ruined Village",   "x": 500, "y": 200},
    {"name": "Mountain Pass",    "x": 800, "y": 350},
]


class MapScene:
    def __init__(self):
        self.font       = pygame.font.SysFont("monospace", 20)
        self.small_font = pygame.font.SysFont("monospace", 14)

        self.location_menu = Menu(
            options=[loc["name"] for loc in LOCATIONS],
            on_confirm=self._on_location_confirm,
        )
        self._manager = None

    # --- Callbacks ---

    def _on_location_confirm(self, name):
        enemies = LOCATION_ENEMIES[name]()
        self._manager.set_scene(BattleScene(self._manager.state, enemies))

    # --- Scene interface ---

    def handle_event(self, event, manager):
        if event.type != pygame.KEYDOWN:
            return
        self.location_menu.handle_key(event.key)

    def update(self, manager):
        self._manager = manager

    def draw(self, screen):
        screen.fill((10, 20, 40))
        w, h = screen.get_width(), screen.get_height()

        for i, loc in enumerate(LOCATIONS):
            active = (i == self.location_menu.selected)
            color  = YELLOW if active else GRAY
            radius = 16 if active else 10
            pygame.draw.circle(screen, color, (loc["x"], loc["y"]), radius)
            label = self.small_font.render(loc["name"], True, color)
            screen.blit(label, (loc["x"] - label.get_width() // 2, loc["y"] + 20))

        title = self.font.render(f"> {self.location_menu.current}", True, WHITE)
        screen.blit(title, (w // 2 - title.get_width() // 2, 680))

        hint = self.small_font.render("LEFT/RIGHT: locatie   ENTER: ga   M/TAB: menu", True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 20))
