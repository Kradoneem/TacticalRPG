import pygame

WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GREEN  = (80,  200,  80)
GRAY   = (120, 120, 120)
BLACK  = (0,     0,   0)
DIM    = (40,   40,  40)
CYAN   = (100, 220, 255)
RED    = (200,  80,  80)
BLUE   = (30,   80, 200)

STAT_LABELS = ["max_hp", "attack", "defense", "speed", "wisdom"]
STAT_SHORT  = {
    "max_hp":   "HP",
    "attack":   "ATK",
    "defense":  "DEF",
    "speed":    "SPD",
    "wisdom":   "WIS",
}


class BattleResultsScene:
    """
    Shown after a victory.
    - Distributes XP to living party members
    - Shows level-up stat changes per unit
    - Displays XP bar progress
    - Auto-saves on exit
    ENTER continues to MapScene.
    """

    def __init__(self, state, defeated_enemies: list):
        self.state = state
        self.font  = pygame.font.SysFont("monospace", 20)
        self.small = pygame.font.SysFont("monospace", 16)
        self.tiny  = pygame.font.SysFont("monospace", 13)

        self.results = self._calculate_results(defeated_enemies)

    # --- XP berekening ---

    def _calculate_results(self, defeated_enemies: list) -> list[dict]:
        total_exp = sum(
            e.max_hp + e.attack + e.defense + e.speed + e.wisdom
            for e in defeated_enemies
        )

        results = []
        for unit in self.state.party:
            if not unit.is_alive():
                results.append({
                    "name":       unit.name,
                    "exp_gained": 0,
                    "level":      unit.level,
                    "alive":      False,
                    "leveled":    False,
                    "level_log":  [],
                    "old_stats":  None,
                    "new_stats":  None,
                    "xp_before":  unit.exp,
                    "xp_after":   unit.exp,
                    "xp_needed":  unit.level * 100,
                })
                continue

            xp_before  = unit.exp
            level_before = unit.level
            old_stats  = {s: getattr(unit, s) for s in STAT_LABELS}

            # gain_xp verwerkt level-ups intern en geeft log-regels terug
            level_log  = unit.gain_xp(total_exp)

            leveled    = unit.level > level_before
            new_stats  = {s: getattr(unit, s) for s in STAT_LABELS}

            results.append({
                "name":       unit.name,
                "exp_gained": total_exp,
                "level":      unit.level,
                "alive":      True,
                "leveled":    leveled,
                "level_log":  level_log,
                "old_stats":  old_stats,
                "new_stats":  new_stats,
                "xp_before":  xp_before,
                "xp_after":   unit.exp,
                "xp_needed":  unit.level * 100,
            })

        return results

    # --- Scene interface ---

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            manager.save()
            from map_scene import MapScene
            manager.set_scene(MapScene())

    def update(self, manager):
        pass

    def draw(self, screen):
        screen.fill((10, 20, 40))
        w, h = screen.get_width(), screen.get_height()

        # --- Titel ---
        title = self.font.render("✦ VICTORY ✦", True, YELLOW)
        screen.blit(title, (w // 2 - title.get_width() // 2, 30))

        sub = self.small.render("Battle Results", True, WHITE)
        screen.blit(sub, (w // 2 - sub.get_width() // 2, 62))

        pygame.draw.line(screen, GRAY, (60, 92), (w - 60, 92), 1)

        # --- Per unit ---
        y = 110
        for r in self.results:
            y = self._draw_unit_result(screen, r, y, w)
            y += 12

        # --- Hint ---
        hint = self.small.render("ENTER: back to map  (auto-save)", True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 36))

    def _draw_unit_result(self, screen, r: dict, y: int, w: int) -> int:
        """Tekent één unit-blok. Geeft nieuwe y terug."""

        alive = r["alive"]
        color = WHITE if alive else GRAY

        # Naam + level
        name_surf = self.font.render(
            f"{r['name']}  Lv.{r['level']}", True, color)
        screen.blit(name_surf, (80, y))

        if not alive:
            ko = self.small.render("K.O. — no XP", True, RED)
            screen.blit(ko, (340, y + 4))
            return y + 40

        # XP gained
        xp_surf = self.small.render(f"+{r['exp_gained']} XP", True, GREEN)
        screen.blit(xp_surf, (340, y + 4))

        # Level-up badge
        if r["leveled"]:
            lv = self.font.render("LEVEL UP!", True, YELLOW)
            screen.blit(lv, (500, y))

        y += 30

        # XP balk
        bar_x, bar_w, bar_h = 80, 400, 10
        xp_needed = r["xp_needed"]
        xp_after  = r["xp_after"]
        filled    = int(bar_w * (xp_after / xp_needed)) if xp_needed > 0 else 0
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, y, bar_w, bar_h))
        pygame.draw.rect(screen, CYAN,         (bar_x, y, filled, bar_h))
        pygame.draw.rect(screen, GRAY,         (bar_x, y, bar_w, bar_h), 1)

        xp_label = self.tiny.render(
            f"XP {xp_after}/{xp_needed}", True, GRAY)
        screen.blit(xp_label, (bar_x + bar_w + 10, y - 1))

        y += 18

        # Stat-vergelijking bij level-up
        if r["leveled"] and r["old_stats"] and r["new_stats"]:
            cols   = 5
            col_w  = 120
            start_x = 80
            for i, stat in enumerate(STAT_LABELS):
                old   = r["old_stats"][stat]
                new   = r["new_stats"][stat]
                diff  = new - old
                label = STAT_SHORT[stat]
                sx    = start_x + i * col_w

                screen.blit(self.tiny.render(f"{label}", True, GRAY),
                            (sx, y))
                screen.blit(self.tiny.render(f"{old}→{new}", True, WHITE),
                            (sx, y + 14))
                if diff > 0:
                    screen.blit(self.tiny.render(f"+{diff}", True, CYAN),
                                (sx, y + 28))
            y += 48

        return y
