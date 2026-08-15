import pygame
from menu import Menu

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GRAY   = (80,   80,  80)
DIM    = (40,   40,  40)
PANEL  = (20,  20,  50)


class ItemMenuOverlay:
    """
    Herbruikbaar item-menu overlay voor in en buiten battle.

    Gebruik:
        overlay = ItemMenuOverlay(items, party, on_done)
        overlay.handle_key(key)
        overlay.draw(screen)

    on_done(log: str) wordt aangeroepen na gebruik of annulering.
    Bij annulering is log een lege string.
    """

    def __init__(self, items: list, party: list, on_done):
        self.items   = items    # referentie naar state.items
        self.party   = party    # referentie naar state.party
        self.on_done = on_done  # callback(log: str)

        self.font       = pygame.font.SysFont("monospace", 16)
        self.small_font = pygame.font.SysFont("monospace", 14)

        self._phase         = "item"    # "item" | "target"
        self._selected_item = None

        self.item_menu = Menu(
            options=list(items),
            on_confirm=self._on_item_confirm,
            on_cancel=self._on_cancel,
        )
        self.target_menu = Menu(
            options=[],
            on_confirm=self._on_target_confirm,
            on_cancel=self._on_target_cancel,
        )

    @property
    def active_menu(self):
        return self.item_menu if self._phase == "item" else self.target_menu

    def handle_key(self, key):
        self.active_menu.handle_key(key)

    # --- Callbacks ---

    def _on_item_confirm(self, item):
        if not self.items:
            return

        self._selected_item = item

        if item.target == "all":
            # Geen target nodig — direct toepassen
            self._apply_to_all(item)
        else:
            # Target kiezen uit levende party-leden
            self.target_menu.options  = [u for u in self.party if u.is_alive()]
            self.target_menu.selected = 0
            self._phase = "target"

    def _on_target_confirm(self, unit):
        item = self._selected_item
        log  = item.use_on(unit)
        self.items.remove(item)
        self._phase = "item"
        self.item_menu.options = list(self.items)
        self.on_done(log)

    def _on_target_cancel(self):
        self._phase = "item"

    def _on_cancel(self):
        self.on_done("")   # lege string = geannuleerd

    def _apply_to_all(self, item):
        logs = []
        for unit in self.party:
            if unit.is_alive():
                logs.append(item.use_on(unit))
        self.items.remove(item)
        self.item_menu.options = list(self.items)
        self.on_done(" | ".join(logs))

    # --- Draw ---

    def draw(self, screen):
        w, h = screen.get_width(), screen.get_height()

        # Semi-transparant paneel
        panel = pygame.Surface((500, 340))
        panel.set_alpha(220)
        panel.fill(PANEL)
        px = w // 2 - 250
        py = h // 2 - 170
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, YELLOW, (px, py, 500, 340), 2)

        if self._phase == "item":
            self._draw_item_list(screen, px, py)
        else:
            self._draw_target_list(screen, px, py)

    def _draw_item_list(self, screen, px, py):
        title = self.font.render("── Items ──", True, YELLOW)
        screen.blit(title, (px + 20, py + 16))

        if not self.items:
            empty = self.font.render("No items in inventory.", True, GRAY)
            screen.blit(empty, (px + 20, py + 60))
            hint = self.small_font.render("ESC: close", True, DIM)
            screen.blit(hint, (px + 20, py + 310))
            return

        for i, item in enumerate(self.items):
            color  = YELLOW if i == self.item_menu.selected else WHITE
            prefix = "> " if i == self.item_menu.selected else "  "
            line   = self.font.render(f"{prefix}[{i+1}] {item.name}", True, color)
            screen.blit(line, (px + 20, py + 50 + i * 26))

        # Beschrijving geselecteerd item
        sel = self.item_menu.current
        if sel and sel.description:
            desc = self.small_font.render(sel.description, True, GRAY)
            screen.blit(desc, (px + 20, py + 290))

        hint = self.small_font.render("↑↓ navigeren   ENTER: gebruik   ESC: sluiten", True, DIM)
        screen.blit(hint, (px + 20, py + 314))

    def _draw_target_list(self, screen, px, py):
        item = self._selected_item
        title = self.font.render(f"── {item.name}: kies target ──", True, YELLOW)
        screen.blit(title, (px + 20, py + 16))

        for i, unit in enumerate(self.target_menu.options):
            color  = YELLOW if i == self.target_menu.selected else WHITE
            prefix = "> " if i == self.target_menu.selected else "  "
            line   = self.font.render(
                f"{prefix}{unit.name}  HP {unit.hp}/{unit.max_hp}  MP {unit.mp}/{unit.max_mp}",
                True, color
            )
            screen.blit(line, (px + 20, py + 50 + i * 30))

        hint = self.small_font.render("↑↓ navigeren   ENTER: bevestig   ESC: terug", True, DIM)
        screen.blit(hint, (px + 20, py + 314))
