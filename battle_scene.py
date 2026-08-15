import pygame
from unit import Unit
from equipment import Equipment
from menu import Menu
from battle import Battle

# --- Kleuren ---
BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
RED       = (255,   0,   0)
YELLOW    = (255, 220,   0)
DARK_BLUE = (20,  20,  60)
BLUE      = (30,  80, 200)

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 800

# Unit card afmetingen
CARD_W = 160
CARD_H = 100   # iets hoger dan voorheen om MP-balk te passen


class BattleScene:
    def __init__(self, state, enemies: list):
        self.font = pygame.font.SysFont("monospace", 16)

        actions = ["Attack", "Heal", "Defend", "Wait"]
        self.action_menu = Menu(options=actions, on_confirm=self.confirm_action)
        self.target_menu = Menu(options=[], on_confirm=self.confirm_target,
                                on_cancel=self.cancel_target)

        self.battle         = None
        self.current_unit   = None
        self.battle_log     = []
        self.battle_over    = False
        self.battle_outcome = ""
        self.active_menu    = None

        self.init_battle(state, enemies)

    # --- Setup ---

    def init_battle(self, state, enemies: list):
        self._state   = state
        self._enemies = enemies

        self.battle         = Battle(team=state.party, enemies=enemies)
        self.current_unit   = state.party[0]
        self.battle_log     = []
        self.battle_over    = False
        self.battle_outcome = ""
        self.active_menu    = self.action_menu
        self.action_menu.selected = 0

    # --- Acties ---

    def confirm_action(self, action):
        if action in ["Attack", "Heal"]:
            if action == "Attack":
                self.target_menu.options = [e for e in self.battle.enemies if e.is_alive()]
            elif action == "Heal":
                self.target_menu.options = [u for u in self.battle.team if u.is_alive()]
            self.target_menu.selected = 0
            self.active_menu = self.target_menu
        else:
            log = self.battle.resolve_turn(self.current_unit, action, target=None)
            self.battle_log.extend(log)
            self.battle_log = self.battle_log[-5:]

    def confirm_target(self, target):
        log = self.battle.resolve_turn(self.current_unit, self.action_menu.current,
                                       target=target)
        self.battle_log.extend(log)
        self.battle_log = self.battle_log[-5:]
        self.active_menu = self.action_menu

    def cancel_target(self):
        self.active_menu = self.action_menu

    # --- Helpers ---

    def is_targeted(self, unit):
        return (
            self.active_menu == self.target_menu and
            unit in self.target_menu.options and
            self.target_menu.options.index(unit) == self.target_menu.selected
        )

    # --- Draw helpers ---

    def draw_bar(self, surface, x, y, width, height, current, maximum, color):
        """Tekent een gekleurde balk met zwarte achtergrond."""
        filled = int(width * (current / maximum)) if maximum > 0 else 0
        pygame.draw.rect(surface, BLACK,  (x, y, width,  height))
        pygame.draw.rect(surface, color,  (x, y, filled, height))

    def draw_unit(self, surface, unit, x, y, card_color, selected=False):
        pygame.draw.rect(surface, card_color, (x, y, CARD_W, CARD_H))
        if selected:
            pygame.draw.rect(surface, YELLOW, (x, y, CARD_W, CARD_H), 3)

        # Naam
        name_surf = self.font.render(unit.name, True, WHITE)
        surface.blit(name_surf, (x + 8, y + 6))

        # HP tekst + balk
        hp_pct   = unit.hp / unit.max_hp
        hp_color = (200, 0, 0) if hp_pct < 0.5 else (0, 200, 0)
        hp_surf  = self.font.render(f"HP {unit.hp}/{unit.max_hp}", True, WHITE)
        surface.blit(hp_surf, (x + 8, y + 26))
        self.draw_bar(surface, x + 8, y + 44, 144, 10, unit.hp, unit.max_hp, hp_color)

        # MP tekst + balk
        mp_surf = self.font.render(f"MP {unit.mp}/{unit.max_mp}", True, WHITE)
        surface.blit(mp_surf, (x + 8, y + 58))
        self.draw_bar(surface, x + 8, y + 76, 144, 10, unit.mp, unit.max_mp, BLUE)

    def draw_menu(self, surface):
        menu_x = 80
        menu_y = 740
        options = (
            [u.name for u in self.active_menu.options]
            if self.active_menu == self.target_menu
            else self.active_menu.options
        )
        for i, option in enumerate(options):
            color = YELLOW if i == self.active_menu.selected else WHITE
            text  = self.font.render(f"[{i+1}] {option}", True, color)
            surface.blit(text, (menu_x + i * 200, menu_y))

    def draw_log(self, surface):
        log_x = 80
        log_y = 530
        for i, line in enumerate(self.battle_log):
            text = self.font.render(line, True, WHITE)
            surface.blit(text, (log_x, log_y + i * 22))

    # --- Scene interface ---

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN:
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
            self.active_menu.handle_key(event.key)

    def update(self, manager):
        if self.battle.is_over() and not self.battle_over:
            self.battle_over    = True
            self.battle_outcome = self.battle.outcome()

    def draw(self, screen):
        screen.fill(BLACK)

        enemy_positions = [(80, 80),  (260, 80),  (440, 80),  (620, 80)]
        ally_positions  = [(80, 620), (260, 620), (440, 620), (620, 620)]

        for unit, (x, y) in zip(self.battle.enemies, enemy_positions):
            self.draw_unit(screen, unit, x, y,
                           card_color=(160, 40, 40), selected=self.is_targeted(unit))

        for unit, (x, y) in zip(self.battle.team, ally_positions):
            self.draw_unit(screen, unit, x, y,
                           card_color=(30, 80, 160), selected=self.is_targeted(unit))

        self.draw_menu(screen)
        self.draw_log(screen)

        if self.battle_over:
            if self.battle_outcome == "victory":
                msg, color = "VICTORY!", YELLOW
                sub = "Press Enter to view the results"
            else:
                msg, color = "DEFEAT...", RED
                sub = "Press R to restart or ESC for title"

            text = self.font.render(msg, True, color)
            sub_text = self.font.render(sub, True, WHITE)
            screen.blit(text,     (SCREEN_WIDTH // 2 - text.get_width()     // 2, SCREEN_HEIGHT // 2))
            screen.blit(sub_text, (SCREEN_WIDTH // 2 - sub_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
