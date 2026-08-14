import pygame

WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GREEN  = (80,  200,  80)
GRAY   = (120, 120, 120)
BLACK  = (0,     0,   0)
DIM    = (40,   40,  40)
CYAN   = (100, 220, 255)

STAT_LABELS = ["max_hp", "attack", "defense", "speed", "wisdom"]
STAT_SHORT  = {"max_hp": "HP", "attack": "ATK", "defense": "DEF", "speed": "SPD", "wisdom": "WIS"}


class BattleResultsScene:
    """
    Shown after a victory. Handles XP distribution and level-ups.
    Displays old vs new stats when a unit levels up.
    ENTER continues to MapScene.
    """

    def __init__(self, state, defeated_enemies: list):
        self.state  = state
        self.font   = pygame.font.SysFont("monospace", 20)
        self.small  = pygame.font.SysFont("monospace", 16)
        self.tiny   = pygame.font.SysFont("monospace", 13)

        self.results = self._calculate_results(defeated_enemies)

    def _calculate_results(self, defeated_enemies: list) -> list[dict]:
        total_exp = sum(
            e.max_hp + e.attack + e.defense + e.speed + e.wisdom
            for e in defeated_enemies
        )

        results = []
        for unit in self.state.party:
            if not unit.is_alive():
                results.append({
                    "name":      unit.name,
                    "exp":       0,
                    "leveled":   False,
                    "level":     unit.level,
                    "alive":     False,
                    "old_stats": None,
                    "new_stats": None,
                })
                continue

            gained    = unit.gain_xp(total_exp)
            leveled   = False
            old_stats = None
            new_stats = None

            if gained:
                old_stats = {s: getattr(unit, s) for s in STAT_LABELS}
                unit.levelup()
                new_stats = {s: getattr(unit, s) for s in STAT_LABELS}
                leveled   = True

            results.append({
                "name":      unit.name,
                "exp":       total_exp,
                "leveled":   leveled,
                "level":     unit.level,
                "alive":     True,
                "old_stats": old_stats,
                "new_stats": new_stats,
            })

        return results

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            from map_scene import MapScene
            manager.set_scene(MapScene())

    def update(self, manager):
        pass

    def draw(self, screen):
        screen.fill((10, 20, 40))
        w, h = screen.get_width(), screen.get_height()

        # --- Titel ---
        title = self.font.render("VICTORY!", True, YELLOW)
        screen.blit(title, (w // 2 - title.get_width() // 2, 40))

        sub = self.small.render("Battle Results", True, WHITE)
        screen.blit(sub, (w // 2 - sub.get_width() // 2, 76))

        # --- Per unit ---
        y = 130
        for r in self.results:
            color = GRAY if not r["alive"] else WHITE

            name_surf = self.font.render(r["name"], True, color)
            screen.blit(name_surf, (80, y))

            if r["alive"]:
                exp_surf = self.small.render(f"+{r['exp']} XP", True, GREEN)
                screen.blit(exp_surf, (320, y + 4))

                if r["leveled"]:
                    lv_surf = self.font.render(f"LEVEL UP! → Lv.{r['level']}", True, YELLOW)
                    screen.blit(lv_surf, (480, y))

                    stat_y = y + 28
                    for stat in STAT_LABELS:
                        old   = r["old_stats"][stat]
                        new   = r["new_stats"][stat]
                        diff  = new - old
                        label = STAT_SHORT[stat]

                        screen.blit(self.tiny.render(f"{label}: {old}", True, GRAY),  (480, stat_y))
                        screen.blit(self.tiny.render("→",               True, WHITE), (570, stat_y))
                        screen.blit(self.tiny.render(str(new),          True, WHITE), (590, stat_y))
                        screen.blit(self.tiny.render(f"(+{diff})",      True, CYAN),  (630, stat_y))
                        stat_y += 18

                    y = stat_y + 16   # dynamische y na stat-blok

                else:
                    lv_surf = self.small.render(f"Lv.{r['level']}", True, GRAY)
                    screen.blit(lv_surf, (480, y + 4))
                    y += 52

            else:
                ko_surf = self.small.render("K.O. — geen XP", True, GRAY)
                screen.blit(ko_surf, (320, y + 4))
                y += 52

        # --- Hint ---
        hint = self.small.render("ENTER: terug naar map", True, DIM)
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 40))
