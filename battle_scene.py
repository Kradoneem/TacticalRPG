import pygame
from menu import Menu
from battle import Battle

BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
RED       = (255,   0,   0)
YELLOW    = (255, 220,   0)
GRAY      = (80,  80,  80)
DIM       = (40,  40,  40)
BLUE      = (30,  80,  200)

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 800
CARD_W        = 160
CARD_H        = 100
LOG_MAX_LINES = 8
LOG_FONT_SIZE = 16
LOG_LINE_H    = 20
LOG_Y         = 460


class BattleScene:
    def __init__(self, state, enemies: list):
        self.font     = pygame.font.SysFont("monospace", 16)
        self.log_font = pygame.font.SysFont("monospace", LOG_FONT_SIZE)

        self.battle         = None
        self.current_unit   = None
        self.battle_log     = []
        self.battle_over    = False
        self.battle_outcome = ""

        self._menu_stack    = []
        self._pending_skill = None

        self.init_battle(state, enemies)

    # --- Setup ---

    def init_battle(self, state, enemies: list):
        self._state   = state
        self._enemies = enemies

        self.battle         = Battle(team=state.party, enemies=enemies, state=state)
        self.current_unit   = state.party[0]
        self.battle_log     = []
        self.battle_over    = False
        self.battle_outcome = ""
        self._pending_skill = None
        self._menu_stack    = []
        self._build_action_menu()

    # --- Menu builders ---

    def _build_action_menu(self):
        unit    = self.current_unit
        options = ["Attack"]
        if unit.learned_skills:
            options.append("Skills")
        if unit.learned_spells:
            options.append("Spells")
        options += ["Defend", "Wait"]

        self._menu_stack = [Menu(
            options    = options,
            on_confirm = self._on_action,
            on_cancel  = lambda _=None: None,
        )]

    def _build_skill_menu(self, skills: list, label: str):
        self._menu_stack.append(Menu(
            options    = skills,
            on_confirm = self._on_skill_chosen,
            on_cancel  = self._pop_menu,
        ))

    def _build_target_menu(self, targets: list):
        self._menu_stack.append(Menu(
            options    = targets,
            on_confirm = self._on_target_chosen,
            on_cancel  = self._pop_menu,
        ))

    def _pop_menu(self, _=None):
        if len(self._menu_stack) > 1:
            self._menu_stack.pop()
            self._pending_skill = None

    @property
    def _active_menu(self):
        return self._menu_stack[-1]

    # --- Callbacks ---

    def _on_action(self, action):
        if action == "Attack":
            targets = [e for e in self.battle.enemies if e.is_alive()]
            self._build_target_menu(targets)
        elif action == "Skills":
            self._build_skill_menu(self.current_unit.learned_skills, "Skills")
        elif action == "Spells":
            self._build_skill_menu(self.current_unit.learned_spells, "Spells")
        else:
            log = self.battle.resolve_turn(self.current_unit, action)
            self._add_log(log)

    def _on_skill_chosen(self, skill):
        ok, reason = skill.can_use(self.current_unit, self._state)
        if not ok:
            self._add_log([f"Can't use {skill.name}: {reason}"])
            return

        self._pending_skill = skill

        if skill.target in ("all_enemies", "all_allies", "self"):
            log = self.battle.resolve_turn(
                self.current_unit, skill.category.capitalize(), skill=skill)
            self._add_log(log)
            self._pending_skill = None
            self._build_action_menu()
        elif skill.target == "single_enemy":
            targets = [e for e in self.battle.enemies if e.is_alive()]
            self._build_target_menu(targets)
        elif skill.target == "single_ally":
            targets = [u for u in self.battle.team if u.is_alive()]
            self._build_target_menu(targets)

    def _on_target_chosen(self, target):
        if self._pending_skill:
            action = self._pending_skill.category.capitalize()
            log = self.battle.resolve_turn(
                self.current_unit, action,
                target=target, skill=self._pending_skill)
        else:
            log = self.battle.resolve_turn(
                self.current_unit, "Attack", target=target)
        self._add_log(log)
        self._pending_skill = None
        self._build_action_menu()

    # --- Item callback ---

    def on_item_used(self, log: str):
        if log:
            self._add_log([log])
            other_log = self.battle.resolve_other_turns(self.current_unit)
            self._add_log(other_log)

    def _add_log(self, lines: list):
        self.battle_log.extend(lines)
        self.battle_log = self.battle_log[-LOG_MAX_LINES:]

    # --- Helpers ---

    def _is_target_menu(self) -> bool:
        """True als het actieve menu Unit-objecten bevat."""
        opts = self._active_menu.options
        return bool(opts) and hasattr(opts[0], "hp")

    def _is_targeted(self, unit) -> bool:
        if not self._is_target_menu():
            return False
        menu = self._active_menu
        return (unit in menu.options and
                menu.options.index(unit) == menu.selected)

    # --- Draw helpers ---

    def _draw_bar(self, surface, x, y, w, h, current, maximum, color):
        filled = int(w * (current / maximum)) if maximum > 0 else 0
        pygame.draw.rect(surface, BLACK, (x, y, w, h))
        pygame.draw.rect(surface, color, (x, y, filled, h))

    def _draw_unit_card(self, surface, unit, x, y, card_color, selected=False):
        pygame.draw.rect(surface, card_color, (x, y, CARD_W, CARD_H))
        if selected:
            pygame.draw.rect(surface, YELLOW, (x, y, CARD_W, CARD_H), 3)

        surface.blit(self.font.render(unit.name, True, WHITE), (x + 8, y + 6))

        hp_color = (200, 0, 0) if unit.hp / unit.max_hp < 0.5 else (0, 200, 0)
        surface.blit(self.font.render(f"HP {unit.hp}/{unit.max_hp}", True, WHITE),
                     (x + 8, y + 26))
        self._draw_bar(surface, x + 8, y + 44, 144, 10, unit.hp, unit.max_hp, hp_color)

        surface.blit(self.font.render(f"MP {unit.mp}/{unit.max_mp}", True, WHITE),
                     (x + 8, y + 58))
        self._draw_bar(surface, x + 8, y + 76, 144, 10, unit.mp, unit.max_mp, BLUE)

    def _draw_menu(self, surface):
        # Target-menu: geen tekst, alleen de highlight op de cards doet het werk
        if self._is_target_menu():
            return

        menu   = self._active_menu
        menu_x = 80
        menu_y = 740

        for i, option in enumerate(menu.options):
            active = (i == menu.selected)
            color  = YELLOW if active else WHITE

            if hasattr(option, "mp_cost"):
                # Skill of spell
                cost_parts = []
                if option.mp_cost: cost_parts.append(f"{option.mp_cost}MP")
                if option.hp_cost: cost_parts.append(f"{option.hp_cost}HP")
                cost  = f" ({'/'.join(cost_parts)})" if cost_parts else ""
                ok, _ = option.can_use(self.current_unit, self._state)
                color = color if ok else GRAY
                label = f"{option.name}{cost}"
            else:
                # Actie-string
                label = option

            surface.blit(
                self.font.render(f"[{i+1}] {label}", True, color),
                (menu_x + i * 220, menu_y)
            )

        # Beschrijving van geselecteerde skill
        sel = menu.options[menu.selected] if menu.options else None
        if sel and hasattr(sel, "description") and sel.description:
            surface.blit(
                self.font.render(sel.description, True, DIM),
                (menu_x, menu_y - 24)
            )

    def _draw_log(self, surface):
        for i, line in enumerate(self.battle_log):
            surface.blit(
                self.log_font.render(line, True, WHITE),
                (80, LOG_Y + i * LOG_LINE_H)
            )

    # --- Scene interface ---

    def handle_event(self, event, manager):
        if event.type != pygame.KEYDOWN:
            return

        manager.party_menu.on_item_used = self.on_item_used

        if self.battle_over:
            if self.battle_outcome == "victory":
                if event.key == pygame.K_RETURN:
                    from battle_results_scene import BattleResultsScene
                    manager.set_scene(
                        BattleResultsScene(self._state, list(self.battle._defeated))
                    )
            else:
                if event.key == pygame.K_r:
                    self.init_battle(self._state, self._enemies)
                elif event.key == pygame.K_ESCAPE:
                    from title_scene import TitleScene
                    manager.set_scene(TitleScene())
            return

        self._active_menu.handle_key(event.key)

    def update(self, manager):
        if self.battle.is_over() and not self.battle_over:
            self.battle_over    = True
            self.battle_outcome = self.battle.outcome()

    def draw(self, screen):
        screen.fill(BLACK)

        enemy_positions = [(80, 80),  (260, 80),  (440, 80),  (620, 80)]
        ally_positions  = [(80, 620), (260, 620), (440, 620), (620, 620)]

        for unit, (x, y) in zip(self.battle.enemies, enemy_positions):
            self._draw_unit_card(screen, unit, x, y,
                                 card_color=(160, 40, 40),
                                 selected=self._is_targeted(unit))

        for unit, (x, y) in zip(self.battle.team, ally_positions):
            self._draw_unit_card(screen, unit, x, y,
                                 card_color=(30, 80, 160),
                                 selected=self._is_targeted(unit))

        self._draw_menu(screen)
        self._draw_log(screen)

        if self.battle_over:
            if self.battle_outcome == "victory":
                msg, color = "VICTORY!", YELLOW
                sub = "Press Enter to view the results"
            else:
                msg, color = "DEFEAT...", RED
                sub = "Press R to restart or ESC for title"

            text     = self.font.render(msg, True, color)
            sub_text = self.font.render(sub, True, WHITE)
            screen.blit(text,
                        (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(sub_text,
                        (SCREEN_WIDTH // 2 - sub_text.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 40))
