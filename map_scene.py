import pygame
from battle_scene import BattleScene
from menu import Menu
from unit import Unit

LOCATION_ENEMIES = {
    "Forest Outskirts": lambda: [
        Unit("Goblin", level=1, hp=20, attack=8,  defense=2, speed=5, wisdom=2, mp=0),
        Unit("Orc",    level=2, hp=35, attack=10, defense=4, speed=3, wisdom=1, mp=0),
    ],
    "Ruined Village": lambda: [
        Unit("Bandit",    level=2, hp=25, attack=10, defense=3, speed=6, wisdom=1, mp=0),
        Unit("Dark Mage", level=2, hp=18, attack=14, defense=1, speed=7, wisdom=8, mp=20),
    ],
    "Mountain Pass": lambda: [
        Unit("Stone Troll", level=3, hp=50, attack=12, defense=6, speed=2, wisdom=1, mp=0),
    ],
}

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GRAY   = (80,   80,  80)
DIM    = (40,   40,  40)
GREEN  = (80,  200,  80)

LOCATIONS = [
    {"name": "Forest Outskirts", "x": 200, "y": 300},
    {"name": "Ruined Village",   "x": 500, "y": 200},
    {"name": "Mountain Pass",    "x": 800, "y": 350},
]


class MapScene:
    def __init__(self):
        self.font       = pygame.font.SysFont("monospace", 20)
        self.small_font = pygame.font.SysFont("monospace", 14)
        self.focus_row  = 0

        self._manager    = None
        self._save_flash = 0   # frames om "Saved!" te tonen

        self.location_menu = Menu(
            options=[loc["name"] for loc in LOCATIONS],
            on_confirm=self._on_location_confirm,
        )

        self.button_menu = Menu(
            options=["Equipment", "Save"],
            on_confirm=self._on_button_confirm,
            on_cancel=self._focus_locations,
        )

    # --- Callbacks ---

    def _on_location_confirm(self, name):
        enemies = LOCATION_ENEMIES[name]()
        self._manager.set_scene(BattleScene(self._manager.state, enemies))

    def _on_button_confirm(self, name):
        if name == "Equipment":
            from equipment_scene import EquipmentScene
            self._manager.set_scene(EquipmentScene(self._manager.state))
        elif name == "Save":
            success = self._manager.save()
            if success:
                self._save_flash = 120   # ~2 seconden bij 60fps

    def _focus_locations(self):
        self.focus_row = 0

    # --- Scene interface ---

    def handle_event(self, event, manager):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_DOWN and self.focus_row == 0:
            self.focus_row = 1
            self.button_menu.selected = 0
            return

        if event.key == pygame.K_UP and self.focus_row == 1:
            self.focus_row = 0
            return

        if self.focus_row == 0:
            self.location_menu.handle_key(event.key)
        else:
            self.button_menu.handle_key(event.key)

    def update(self, manager):
        self._manager = manager   # hier cachen, niet in handle_event

        if self._save_flash > 0:
            self._save_flash -= 1

    def draw(self, screen):
        screen.fill((10, 20, 40))
        w, h = screen.get_width(), screen.get_height()

        # --- Locaties ---
        for i, loc in enumerate(LOCATIONS):
            active = (self.focus_row == 0 and i == self.location_menu.selected)
            color  = YELLOW if active else GRAY
            radius = 16 if active else 10
            pygame.draw.circle(screen, color, (loc["x"], loc["y"]), radius)
            label = self.small_font.render(loc["name"], True, color)
            screen.blit(label, (loc["x"] - label.get_width() // 2, loc["y"] + 20))

        # --- Geselecteerde locatienaam midden ---
        if self.focus_row == 0:
            title = self.font.render(f"> {self.location_menu.current}", True, WHITE)
            screen.blit(title, (w // 2 - title.get_width() // 2, 680))

        # --- Knoppen rechtsonder ---
        btn_y       = h - 60
        btn_x_start = w - 260
        for i, label in enumerate(self.button_menu.options):
            active = (self.focus_row == 1 and i == self.button_menu.selected)
            color  = YELLOW if active else GRAY
            text   = self.font.render(f"[{label}]", True, color)
            screen.blit(text, (btn_x_start + i * 130, btn_y))

        # --- Save flash ---
        if self._save_flash > 0:
            saved_surf = self.font.render("Game saved!", True, GREEN)
            screen.blit(saved_surf, (w // 2 - saved_surf.get_width() // 2, h - 90))

        # --- Hint ---
        if self.focus_row == 0:
            hint_text = "LEFT/RIGHT: locatie   DOWN: menu   ENTER: ga"
        else:
            hint_text = "LEFT/RIGHT: keuze   UP/ESC: terug   ENTER: selecteer"
        hint = self.small_font.render(hint_text, True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 20))
