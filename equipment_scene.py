import pygame
from menu import Menu

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GRAY   = (80,  80,  80)
DIM    = (40,  40,  40)
GREEN  = (80,  200, 80)
RED    = (200, 80,  80)

SLOTS = ["weapon", "armor", "accessory"]


class EquipmentScene:
    """
    Three-step equipment screen:
      step 0 — choose unit
      step 1 — choose slot
      step 2 — choose item from inventory (filtered by slot)
    ESC goes back one step. From step 0 ESC returns to MapScene.
    """

    def __init__(self, state):
        self.state      = state
        self.step       = 0
        self.unit       = None   # gekozen unit
        self.slot       = None   # gekozen slot

        self.font       = pygame.font.SysFont("monospace", 20)
        self.small_font = pygame.font.SysFont("monospace", 15)

        self._build_unit_menu()

    # --- Menu builders ---

    def _build_unit_menu(self):
        self.menu = Menu(
            options=[u.name for u in self.state.party],
            on_confirm=self._confirm_unit,
            on_cancel=self._go_back,
        )

    def _build_slot_menu(self):
        self.menu = Menu(
            options=SLOTS,
            on_confirm=self._confirm_slot,
            on_cancel=self._go_back,
        )

    def _build_item_menu(self):
        items = self._filtered_items()
        options = [item.name for item in items]
        if not options:
            options = ["(geen items)"]
        self.menu = Menu(
            options=options,
            on_confirm=self._confirm_item,
            on_cancel=self._go_back,
        )

    def _filtered_items(self) -> list:
        return [item for item in self.state.inventory if item.slot == self.slot]

    # --- Callbacks ---

    def _confirm_unit(self, name):
        self.unit = next(u for u in self.state.party if u.name == name)
        self.step = 1
        self._build_slot_menu()

    def _confirm_slot(self, slot):
        self.slot = slot
        self.step = 2
        self._build_item_menu()

    def _confirm_item(self, name):
        items = self._filtered_items()
        if not items:
            return
        item = next((i for i in items if i.name == name), None)
        if item is None:
            return

        # Unequip bestaand item in slot → terug in inventory
        if self.slot in self.unit.equipment:
            old_item = self.unit.equipment[self.slot]
            self.unit.unequip(self.slot)
            self.state.inventory.append(old_item)

        self.unit.equip(item)
        self.state.inventory.remove(item)

        # Terug naar slot-keuze na equippen
        self.step = 1
        self._build_slot_menu()

    def _go_back(self):
        if self.step == 0:
            self._return_to_map()
        elif self.step == 1:
            self.step = 0
            self.unit = None
            self._build_unit_menu()
        elif self.step == 2:
            self.step = 1
            self.slot = None
            self._build_slot_menu()

    def _return_to_map(self):
        from map_scene import MapScene
        self._manager.set_scene(MapScene())

    # --- Scene interface ---

    def handle_event(self, event, manager):
        self._manager = manager
        if event.type == pygame.KEYDOWN:
            self.menu.handle_key(event.key)

    def update(self, manager):
        pass

    def draw(self, screen):
        screen.fill((10, 20, 40))
        w, h = screen.get_width(), screen.get_height()

        # --- Titel ---
        titles = ["Kies een unit", "Kies een slot", "Kies een item"]
        title = self.font.render(titles[self.step], True, WHITE)
        screen.blit(title, (40, 40))

        # --- Menu opties ---
        for i, option in enumerate(self.menu.options):
            active = (i == self.menu.selected)
            color  = YELLOW if active else GRAY
            prefix = "> " if active else "  "
            text   = self.font.render(f"{prefix}{option}", True, color)
            screen.blit(text, (80, 100 + i * 36))

        # --- Unit stats (rechts) als unit gekozen ---
        if self.unit:
            self._draw_unit_panel(screen, self.unit, w - 380, 80)

        # --- Hint ---
        hint = self.small_font.render("UP/DOWN: navigeer   ENTER: kies   ESC: terug", True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 24))

    def _draw_unit_panel(self, screen, unit, x, y):
        lines = [
            unit.name,
            f"Lv. {unit.level}",
            f"HP:  {unit.hp}/{unit.max_hp}",
            f"ATK: {unit.attack}",
            f"DEF: {unit.defense}",
            f"SPD: {unit.speed}",
            f"WIS: {unit.wisdom}",
            "",
            "Equipped:",
        ]
        for slot in SLOTS:
            item = unit.equipment.get(slot)
            label = item.name if item else "(leeg)"
            color = GREEN if item else GRAY
            lines.append(f"  {slot}: {label}")

        for i, line in enumerate(lines):
            color = WHITE if i < 2 else GRAY
            surf  = self.small_font.render(line, True, color)
            screen.blit(surf, (x, y + i * 22))
