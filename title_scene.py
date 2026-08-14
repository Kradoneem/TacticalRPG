import pygame
from menu import Menu

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
YELLOW = (255, 220,  0)
GRAY   = (120, 120, 120)
DIM    = (40,   40,  40)


class TitleScene:
    """
    Title screen with New Game and (optional) Continue.
    Uses the Menu class for navigation.
    """

    def __init__(self):
        self.font   = pygame.font.SysFont("monospace", 32)
        self.medium = pygame.font.SysFont("monospace", 22)
        self.small  = pygame.font.SysFont("monospace", 16)

        self._has_save   = False
        self._manager    = None   # wordt gezet in update
        self.menu        = None   # wordt aangemaakt zodra manager bekend is

    def _build_menu(self, manager):
        options = ["New Game"]
        if manager.has_save():
            options.append("Continue")

        def on_confirm(choice):
            from map_scene import MapScene
            if choice == "New Game":
                from game_state import GameState
                manager.state = GameState()
                manager.set_scene(MapScene())
            elif choice == "Continue":
                success = manager.load()
                if not success:
                    from game_state import GameState
                    manager.state = GameState()
                manager.set_scene(MapScene())

        return Menu(options=options, on_confirm=on_confirm)

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN:
            self.menu.handle_key(event.key)

    def update(self, manager):
        has_save = manager.has_save()

        # Bouw menu opnieuw als has_save verandert (of eerste keer)
        if self.menu is None or has_save != self._has_save:
            self._has_save = has_save
            self.menu = self._build_menu(manager)

    def draw(self, screen):
        screen.fill(BLACK)
        w, h = screen.get_width(), screen.get_height()

        # --- Titel ---
        title = self.font.render("TacticalRPG", True, YELLOW)
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 3))

        # --- Menu opties ---
        y = h // 3 + 90
        for i, option in enumerate(self.menu.options):
            color  = WHITE if i == self.menu.selected else GRAY
            prefix = "> " if i == self.menu.selected else "  "
            surf   = self.medium.render(f"{prefix}{option}", True, color)
            screen.blit(surf, (w // 2 - surf.get_width() // 2, y))
            y += 44

        # --- Hint ---
        hint = self.small.render("↑↓ navigeren   ENTER bevestigen", True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 40))
