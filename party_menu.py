import pygame
from menu import Menu

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 220,   0)
GRAY   = (80,  80,  80)
DIM    = (40,  40,  40)
GREEN  = (80,  200, 80)
RED    = (200, 80,  80)
BLUE   = (30,  80,  200)
PANEL  = (15,  15,  40)

SLOTS = ["weapon", "armor", "accessory"]
TABS  = ["Party", "Skills", "Items", "Equipment", "System"]


class PartyMenu:
    """
    Universele party overlay. Leeft op SceneManager.
    Openen/sluiten via toggle(). Input via handle_key().

    on_item_used(log: str) — callback die de actieve scene
    afhandelt (beurt verbruiken in battle, niets op map).
    """

    def __init__(self):
        self.font       = pygame.font.SysFont("monospace", 18)
        self.small_font = pygame.font.SysFont("monospace", 14)

        self.open         = False
        self.tab_index    = 0
        self.on_item_used = None   # wordt gezet door de actieve scene

        # --- Party tab ---
        self.party_selected = 0

        # --- Skills tab ---
        self._skill_step     = 0     # 0=unit 1=skill/spell 2=target
        self._skill_unit     = None
        self._skill_selected = None
        self.skill_unit_sel  = 0
        self.skill_sel       = 0
        self.skill_target_sel = 0
        self._skill_list     = []    # actieve lijst (skills + spells gecombineerd)

        # --- Items tab ---
        self._item_phase     = "item"
        self._item_selected  = None
        self.item_selected   = 0
        self.target_selected = 0

        # --- Equipment tab ---
        self._equip_step    = 0
        self._equip_unit    = None
        self._equip_slot    = None
        self.equip_selected = 0

        # --- System tab ---
        self.system_selected = 0
        self._system_options = ["Save", "Load"]
        self._system_flash   = ""
        self._system_flash_t = 0

    # --- Public interface ---

    def toggle(self):
        self.open = not self.open
        if not self.open:
            self._reset_state()

    def handle_key(self, key, state, manager):
        if key == pygame.K_ESCAPE:
            if self._any_substep_active():
                self._back_substep()
            else:
                self.toggle()
            return

        if key == pygame.K_LEFT:
            self.tab_index = (self.tab_index - 1) % len(TABS)
            self._reset_tab_state()
            return
        if key == pygame.K_RIGHT:
            self.tab_index = (self.tab_index + 1) % len(TABS)
            self._reset_tab_state()
            return

        tab = TABS[self.tab_index]
        if tab == "Party":
            self._handle_party(key, state)
        elif tab == "Skills":
            self._handle_skills(key, state)
        elif tab == "Items":
            self._handle_items(key, state)
        elif tab == "Equipment":
            self._handle_equipment(key, state)
        elif tab == "System":
            self._handle_system(key, manager)

    def draw(self, screen, state):
        if not self.open:
            return

        w, h = screen.get_width(), screen.get_height()
        pw, ph = 900, 560
        px = w // 2 - pw // 2
        py = h // 2 - ph // 2

        panel = pygame.Surface((pw, ph))
        panel.set_alpha(235)
        panel.fill(PANEL)
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, YELLOW, (px, py, pw, ph), 2)

        self._draw_tabs(screen, px, py, pw)

        tab = TABS[self.tab_index]
        content_y = py + 50
        if tab == "Party":
            self._draw_party(screen, state, px + 20, content_y, pw)
        elif tab == "Skills":
            self._draw_skills(screen, state, px + 20, content_y, pw)
        elif tab == "Items":
            self._draw_items(screen, state, px + 20, content_y, pw)
        elif tab == "Equipment":
            self._draw_equipment(screen, state, px + 20, content_y, pw)
        elif tab == "System":
            self._draw_system(screen, px + 20, content_y, pw)

        hint = self.small_font.render("◄ ► tab   ESC sluiten", True, DIM)
        screen.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + ph - 22))

        if self._system_flash_t > 0:
            self._system_flash_t -= 1
            flash = self.font.render(self._system_flash, True, GREEN)
            screen.blit(flash, (px + pw // 2 - flash.get_width() // 2, py + ph - 44))

    # =========================================================
    # TABS
    # =========================================================

    def _draw_tabs(self, screen, px, py, pw):
        tab_w = pw // len(TABS)
        for i, tab in enumerate(TABS):
            active = (i == self.tab_index)
            color  = YELLOW if active else GRAY
            bg     = (30, 30, 70) if active else (15, 15, 40)
            tx     = px + i * tab_w
            pygame.draw.rect(screen, bg, (tx, py, tab_w, 30))
            pygame.draw.rect(screen, color, (tx, py, tab_w, 30), 1)
            label = self.font.render(tab, True, color)
            screen.blit(label, (tx + tab_w // 2 - label.get_width() // 2, py + 6))

    # =========================================================
    # PARTY TAB
    # =========================================================

    def _handle_party(self, key, state):
        n = len(state.party)
        if key == pygame.K_UP:
            self.party_selected = (self.party_selected - 1) % n
        elif key == pygame.K_DOWN:
            self.party_selected = (self.party_selected + 1) % n

    def _draw_party(self, screen, state, x, y, pw):
        for i, unit in enumerate(state.party):
            active = (i == self.party_selected)
            color  = YELLOW if active else WHITE
            by     = y + i * 110

            row_color = (30, 30, 70) if active else (20, 20, 50)
            pygame.draw.rect(screen, row_color, (x, by, pw - 40, 100))
            if active:
                pygame.draw.rect(screen, YELLOW, (x, by, pw - 40, 100), 1)

            name = self.font.render(f"{unit.name}  Lv.{unit.level}", True, color)
            screen.blit(name, (x + 12, by + 8))

            self._draw_labeled_bar(screen, x + 12, by + 34, 200, 12,
                                   unit.hp, unit.max_hp,
                                   (0, 180, 0) if unit.hp / unit.max_hp >= 0.5 else RED,
                                   f"HP {unit.hp}/{unit.max_hp}")
            self._draw_labeled_bar(screen, x + 12, by + 58, 200, 12,
                                   unit.mp, unit.max_mp, BLUE,
                                   f"MP {unit.mp}/{unit.max_mp}")

            stats = (f"ATK {unit.attack}  DEF {unit.defense}  "
                     f"SPD {unit.speed}  WIS {unit.wisdom}")
            screen.blit(self.small_font.render(stats, True, GRAY), (x + 260, by + 38))

            equip_parts = []
            for slot in SLOTS:
                item = unit.equipment.get(slot)
                equip_parts.append(item.name if item else f"({slot})")
            screen.blit(self.small_font.render("  ".join(equip_parts), True, DIM),
                        (x + 260, by + 62))

    # =========================================================
    # SKILLS TAB
    # =========================================================

    def _handle_skills(self, key, state):
        party = state.party

        if self._skill_step == 0:
            # Kies unit
            n = len(party)
            if key == pygame.K_UP:
                self.skill_unit_sel = (self.skill_unit_sel - 1) % n
            elif key == pygame.K_DOWN:
                self.skill_unit_sel = (self.skill_unit_sel + 1) % n
            elif key == pygame.K_RETURN:
                self._skill_unit  = party[self.skill_unit_sel]
                self._skill_list  = (self._skill_unit.learned_skills +
                                     self._skill_unit.learned_spells)
                if not self._skill_list:
                    return   # geen skills, niets te doen
                self._skill_step = 1
                self.skill_sel   = 0

        elif self._skill_step == 1:
            # Kies skill/spell
            n = len(self._skill_list)
            if key == pygame.K_UP:
                self.skill_sel = (self.skill_sel - 1) % n
            elif key == pygame.K_DOWN:
                self.skill_sel = (self.skill_sel + 1) % n
            elif key == pygame.K_RETURN:
                skill = self._skill_list[self.skill_sel]
                ok, reason = skill.can_use(self._skill_unit, state)
                if not ok:
                    self._system_flash   = reason
                    self._system_flash_t = 90
                    return
                # Alleen heal-spells bruikbaar buiten battle
                if skill.effect not in ("heal",):
                    self._system_flash   = "Only heal skills usable outside battle."
                    self._system_flash_t = 90
                    return
                self._skill_selected = skill
                if skill.target in ("all_allies",):
                    # Geen target nodig
                    self._use_skill_on_party(state)
                else:
                    self._skill_step      = 2
                    self.skill_target_sel = 0
            elif key == pygame.K_ESCAPE:
                self._skill_step = 0
                self._skill_unit = None

        elif self._skill_step == 2:
            # Kies target
            alive = [u for u in party if u.is_alive()]
            n     = len(alive)
            if key == pygame.K_UP:
                self.skill_target_sel = (self.skill_target_sel - 1) % n
            elif key == pygame.K_DOWN:
                self.skill_target_sel = (self.skill_target_sel + 1) % n
            elif key == pygame.K_RETURN:
                target = alive[self.skill_target_sel]
                skill  = self._skill_selected
                skill.pay_cost(self._skill_unit, state)
                log = skill.apply(self._skill_unit, target, state)
                self._system_flash   = log
                self._system_flash_t = 120
                if self.on_item_used:
                    self.on_item_used(log)
                self._skill_step     = 1
                self._skill_selected = None
            elif key == pygame.K_ESCAPE:
                self._skill_step     = 1
                self._skill_selected = None

    def _use_skill_on_party(self, state):
        skill = self._skill_selected
        logs  = []
        for unit in [u for u in state.party if u.is_alive()]:
            skill.pay_cost(self._skill_unit, state)
            logs.append(skill.apply(self._skill_unit, unit, state))
        combined = " | ".join(logs)
        self._system_flash   = combined[:60]   # past in flash-balk
        self._system_flash_t = 120
        if self.on_item_used:
            self.on_item_used(combined)
        self._skill_step     = 1
        self._skill_selected = None

    def _draw_skills(self, screen, state, x, y, pw):
        if self._skill_step == 0:
            title = self.font.render("── Choose unit ──", True, YELLOW)
            screen.blit(title, (x, y))
            for i, unit in enumerate(state.party):
                active = (i == self.skill_unit_sel)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                n_skills = len(unit.learned_skills)
                n_spells = len(unit.learned_spells)
                label = (f"{prefix}{unit.name}  Lv.{unit.level}"
                         f"   {n_skills} skill(s)  {n_spells} spell(s)")
                screen.blit(self.font.render(label, True, color),
                            (x, y + 36 + i * 32))

        elif self._skill_step in (1, 2):
            unit = self._skill_unit
            # Header
            title = self.font.render(
                f"── {unit.name}: skills & spells ──", True, YELLOW)
            screen.blit(title, (x, y))

            # Stats rechts
            self._draw_unit_stats(screen, unit, x + 500, y)

            skills = self._skill_list
            if not skills:
                screen.blit(self.font.render("No skills learned.", True, GRAY),
                            (x, y + 40))
                return

            for i, skill in enumerate(skills):
                active = (i == self.skill_sel) and self._skill_step == 1
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "

                # Categorie-badge
                badge = "[SP]" if skill.category == "spell" else "[SK]"
                badge_color = BLUE if skill.category == "spell" else GREEN

                # Kosten
                cost_parts = []
                if skill.mp_cost: cost_parts.append(f"{skill.mp_cost}MP")
                if skill.hp_cost: cost_parts.append(f"{skill.hp_cost}HP")
                cost = f"  ({'/'.join(cost_parts)})" if cost_parts else ""

                # Element
                elem = f"  [{'/'.join(skill.elements)}]" if skill.elements else ""

                # Buiten battle bruikbaar?
                usable_outside = skill.effect == "heal"
                avail_color = color if usable_outside else GRAY

                line = self.font.render(
                    f"{prefix}{skill.name}{cost}{elem}", True, avail_color)
                screen.blit(line, (x + 30, y + 36 + i * 28))

                badge_surf = self.small_font.render(badge, True, badge_color)
                screen.blit(badge_surf, (x, y + 38 + i * 28))

            # Beschrijving van geselecteerde skill
            if 0 <= self.skill_sel < len(skills):
                sel = skills[self.skill_sel]
                desc = self.small_font.render(sel.description, True, GRAY)
                screen.blit(desc, (x, y + 36 + len(skills) * 28 + 8))

            # Target-keuze overlay
            if self._skill_step == 2:
                alive = [u for u in state.party if u.is_alive()]
                ty    = y + 36 + len(skills) * 28 + 36
                screen.blit(self.font.render(
                    f"── Use {self._skill_selected.name} on: ──", True, YELLOW),
                    (x, ty))
                for i, unit in enumerate(alive):
                    active = (i == self.skill_target_sel)
                    color  = YELLOW if active else WHITE
                    prefix = "> " if active else "  "
                    line   = self.font.render(
                        f"{prefix}{unit.name}  HP {unit.hp}/{unit.max_hp}"
                        f"  MP {unit.mp}/{unit.max_mp}", True, color)
                    screen.blit(line, (x, ty + 28 + i * 28))

            hint_text = ("↑↓ navigate   ENTER use   ESC back   "
                         "(grey = battle only)")
            screen.blit(self.small_font.render(hint_text, True, DIM), (x, y + 460))

    # =========================================================
    # ITEMS TAB
    # =========================================================

    def _handle_items(self, key, state):
        items = state.items
        party = [u for u in state.party if u.is_alive()]

        if self._item_phase == "item":
            if not items:
                return
            if key == pygame.K_UP:
                self.item_selected = (self.item_selected - 1) % len(items)
            elif key == pygame.K_DOWN:
                self.item_selected = (self.item_selected + 1) % len(items)
            elif key == pygame.K_RETURN:
                item = items[self.item_selected]
                self._item_selected = item
                if item.target == "all":
                    logs = []
                    for unit in party:
                        logs.append(item.use_on(unit))
                    state.items.remove(item)
                    self.item_selected = max(0, self.item_selected - 1)
                    if self.on_item_used:
                        self.on_item_used(" | ".join(logs))
                else:
                    self._item_phase     = "target"
                    self.target_selected = 0

        elif self._item_phase == "target":
            party = [u for u in state.party if u.is_alive()]
            if key == pygame.K_UP:
                self.target_selected = (self.target_selected - 1) % len(party)
            elif key == pygame.K_DOWN:
                self.target_selected = (self.target_selected + 1) % len(party)
            elif key == pygame.K_RETURN:
                unit = party[self.target_selected]
                log  = self._item_selected.use_on(unit)
                state.items.remove(self._item_selected)
                self.item_selected  = max(0, self.item_selected - 1)
                self._item_phase    = "item"
                self._item_selected = None
                if self.on_item_used:
                    self.on_item_used(log)
            elif key == pygame.K_ESCAPE:
                self._item_phase = "item"

    def _draw_items(self, screen, state, x, y, pw):
        items = state.items
        party = [u for u in state.party if u.is_alive()]

        if self._item_phase == "item":
            title = self.font.render("── Items ──", True, YELLOW)
            screen.blit(title, (x, y))
            if not items:
                screen.blit(self.font.render("No items in inventory.", True, GRAY),
                            (x, y + 40))
                return
            for i, item in enumerate(items):
                active = (i == self.item_selected)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                screen.blit(self.font.render(f"{prefix}{item.name}", True, color),
                            (x, y + 36 + i * 28))
            sel = items[self.item_selected] if items else None
            if sel and sel.description:
                screen.blit(self.small_font.render(sel.description, True, GRAY),
                            (x, y + 36 + len(items) * 28 + 10))
            screen.blit(self.small_font.render("↑↓ navigate   ENTER use", True, DIM),
                        (x, y + 460))
        else:
            item = self._item_selected
            screen.blit(self.font.render(
                f"── {item.name}: choose target ──", True, YELLOW), (x, y))
            for i, unit in enumerate(party):
                active = (i == self.target_selected)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                screen.blit(self.font.render(
                    f"{prefix}{unit.name}  HP {unit.hp}/{unit.max_hp}"
                    f"  MP {unit.mp}/{unit.max_mp}", True, color),
                    (x, y + 36 + i * 32))
            screen.blit(self.small_font.render(
                "↑↓ navigate   ENTER confirm   ESC back", True, DIM),
                (x, y + 460))

    # =========================================================
    # EQUIPMENT TAB
    # =========================================================

    def _handle_equipment(self, key, state):
        if self._equip_step == 0:
            n = len(state.party)
            if key == pygame.K_UP:
                self.equip_selected = (self.equip_selected - 1) % n
            elif key == pygame.K_DOWN:
                self.equip_selected = (self.equip_selected + 1) % n
            elif key == pygame.K_RETURN:
                self._equip_unit    = state.party[self.equip_selected]
                self._equip_step    = 1
                self.equip_selected = 0

        elif self._equip_step == 1:
            if key == pygame.K_UP:
                self.equip_selected = (self.equip_selected - 1) % len(SLOTS)
            elif key == pygame.K_DOWN:
                self.equip_selected = (self.equip_selected + 1) % len(SLOTS)
            elif key == pygame.K_RETURN:
                self._equip_slot    = SLOTS[self.equip_selected]
                self._equip_step    = 2
                self.equip_selected = 0
            elif key == pygame.K_ESCAPE:
                self._equip_step    = 0
                self._equip_unit    = None
                self.equip_selected = 0

        elif self._equip_step == 2:
            available = [i for i in state.equipment if i.slot == self._equip_slot]
            options   = available + (
                ["(unequip)"] if self._equip_slot in self._equip_unit.equipment else [])
            if key == pygame.K_UP:
                self.equip_selected = (self.equip_selected - 1) % max(1, len(options))
            elif key == pygame.K_DOWN:
                self.equip_selected = (self.equip_selected + 1) % max(1, len(options))
            elif key == pygame.K_RETURN:
                if not options:
                    return
                choice = options[self.equip_selected]
                if choice == "(unequip)":
                    old = self._equip_unit.equipment[self._equip_slot]
                    self._equip_unit.unequip(self._equip_slot)
                    state.equipment.append(old)
                else:
                    if self._equip_slot in self._equip_unit.equipment:
                        old = self._equip_unit.equipment[self._equip_slot]
                        self._equip_unit.unequip(self._equip_slot)
                        state.equipment.append(old)
                    self._equip_unit.equip(choice)
                    state.equipment.remove(choice)
                self._equip_step    = 1
                self.equip_selected = SLOTS.index(self._equip_slot)
            elif key == pygame.K_ESCAPE:
                self._equip_step    = 1
                self.equip_selected = SLOTS.index(self._equip_slot)

    def _draw_equipment(self, screen, state, x, y, pw):
        if self._equip_step == 0:
            screen.blit(self.font.render("── Choose a unit ──", True, YELLOW), (x, y))
            for i, unit in enumerate(state.party):
                active = (i == self.equip_selected)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                screen.blit(self.font.render(
                    f"{prefix}{unit.name}  Lv.{unit.level}", True, color),
                    (x, y + 36 + i * 32))

        elif self._equip_step == 1:
            unit = self._equip_unit
            screen.blit(self.font.render(
                f"── {unit.name}: choose slot ──", True, YELLOW), (x, y))
            for i, slot in enumerate(SLOTS):
                active = (i == self.equip_selected)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                item   = unit.equipment.get(slot)
                label  = item.name if item else "(empty)"
                icolor = GREEN if item else GRAY
                screen.blit(self.font.render(f"{prefix}{slot}", True, color),
                            (x, y + 36 + i * 32))
                screen.blit(self.small_font.render(label, True, icolor),
                            (x + 160, y + 38 + i * 32))
            self._draw_unit_stats(screen, unit, x + 420, y)

        elif self._equip_step == 2:
            unit      = self._equip_unit
            available = [i for i in state.equipment if i.slot == self._equip_slot]
            options   = available + (
                ["(unequip)"] if self._equip_slot in unit.equipment else [])
            screen.blit(self.font.render(
                f"── {unit.name} / {self._equip_slot} ──", True, YELLOW), (x, y))
            if not options:
                screen.blit(self.font.render("No items available.", True, GRAY),
                            (x, y + 40))
            for i, opt in enumerate(options):
                active = (i == self.equip_selected)
                color  = YELLOW if active else WHITE
                prefix = "> " if active else "  "
                label  = opt if isinstance(opt, str) else opt.name
                screen.blit(self.font.render(f"{prefix}{label}", True, color),
                            (x, y + 36 + i * 32))
            self._draw_unit_stats(screen, unit, x + 420, y)

    def _draw_unit_stats(self, screen, unit, x, y):
        lines = [
            (f"{unit.name}  Lv.{unit.level}", WHITE),
            (f"HP  {unit.hp}/{unit.max_hp}",  GRAY),
            (f"MP  {unit.mp}/{unit.max_mp}",  GRAY),
            (f"ATK {unit.attack}",             GRAY),
            (f"DEF {unit.defense}",            GRAY),
            (f"SPD {unit.speed}",              GRAY),
            (f"WIS {unit.wisdom}",             GRAY),
        ]
        for i, (text, color) in enumerate(lines):
            screen.blit(self.small_font.render(text, True, color), (x, y + i * 22))

    # =========================================================
    # SYSTEM TAB
    # =========================================================

    def _handle_system(self, key, manager):
        n = len(self._system_options)
        if key == pygame.K_UP:
            self.system_selected = (self.system_selected - 1) % n
        elif key == pygame.K_DOWN:
            self.system_selected = (self.system_selected + 1) % n
        elif key == pygame.K_RETURN:
            choice = self._system_options[self.system_selected]
            if choice == "Save":
                ok = manager.save()
                self._system_flash   = "Game saved!" if ok else "Save failed."
                self._system_flash_t = 120
            elif choice == "Load":
                ok = manager.load()
                self._system_flash   = "Game loaded!" if ok else "No save found."
                self._system_flash_t = 120

    def _draw_system(self, screen, x, y, pw):
        screen.blit(self.font.render("── System ──", True, YELLOW), (x, y))
        for i, opt in enumerate(self._system_options):
            active = (i == self.system_selected)
            color  = YELLOW if active else WHITE
            prefix = "> " if active else "  "
            screen.blit(self.font.render(f"{prefix}{opt}", True, color),
                        (x, y + 40 + i * 36))

    # =========================================================
    # HELPERS
    # =========================================================

    def _draw_labeled_bar(self, screen, x, y, w, h, current, maximum, color, label):
        filled = int(w * (current / maximum)) if maximum > 0 else 0
        pygame.draw.rect(screen, BLACK, (x, y, w, h))
        pygame.draw.rect(screen, color, (x, y, filled, h))
        screen.blit(self.small_font.render(label, True, WHITE), (x + w + 8, y - 1))

    def _any_substep_active(self) -> bool:
        tab = TABS[self.tab_index]
        if tab == "Items"     and self._item_phase == "target":    return True
        if tab == "Equipment" and self._equip_step > 0:            return True
        if tab == "Skills"    and self._skill_step > 0:            return True
        return False

    def _back_substep(self):
        tab = TABS[self.tab_index]
        if tab == "Items":
            self._item_phase    = "item"
            self._item_selected = None
        elif tab == "Equipment":
            if self._equip_step == 2:
                self._equip_step    = 1
                self.equip_selected = SLOTS.index(self._equip_slot)
            elif self._equip_step == 1:
                self._equip_step    = 0
                self._equip_unit    = None
                self.equip_selected = 0
        elif tab == "Skills":
            if self._skill_step == 2:
                self._skill_step     = 1
                self._skill_selected = None
            elif self._skill_step == 1:
                self._skill_step = 0
                self._skill_unit = None

    def _reset_tab_state(self):
        self.party_selected   = 0
        self.item_selected    = 0
        self.target_selected  = 0
        self.equip_selected   = 0
        self._item_phase      = "item"
        self._item_selected   = None
        self._equip_step      = 0
        self._equip_unit      = None
        self._equip_slot      = None
        self._skill_step      = 0
        self._skill_unit      = None
        self._skill_selected  = None
        self._skill_list      = []
        self.skill_unit_sel   = 0
        self.skill_sel        = 0
        self.skill_target_sel = 0

    def _reset_state(self):
        self.tab_index = 0
        self._reset_tab_state()
