from unit import Unit


class Battle:
    """
    Manages a tactical battle between two teams.
    Turn order is determined by speed (highest goes first).
    """

    def __init__(self, team: list[Unit], enemies: list[Unit], state=None):
        self.team      = team
        self.enemies   = enemies
        self._state    = state    # nodig voor item_cost checks
        self._defeated = set()

    def _get_turn_order(self) -> list[Unit]:
        all_units = self.team + self.enemies
        return sorted(all_units, key=lambda u: u.speed, reverse=True)

    def _get_target(self, targets: list[Unit]) -> Unit | None:
        living = [u for u in targets if u.is_alive()]
        return min(living, key=lambda u: u.hp) if living else None

    def _team_alive(self, team: list[Unit]) -> bool:
        return any(u.is_alive() for u in team)

    def _check_defeats(self, log: list[str]) -> None:
        for enemy in self.enemies:
            if not enemy.is_alive() and enemy not in self._defeated:
                self._defeated.add(enemy)
                log.append(f"  >> {enemy.name} defeated!")

    # --- Skill/spell resolutie ---

    def _resolve_skill(self, actor: Unit, skill, targets: list[Unit],
                       log: list[str]) -> None:
        """Past een skill/spell toe op één of meerdere targets. Betaalt de cost."""
        ok, reason = skill.can_use(actor, self._state)
        if not ok:
            log.append(f"{actor.name} can't use {skill.name}: {reason}")
            return

        skill.pay_cost(actor, self._state)

        if skill.target in ("single_enemy", "single_ally"):
            target = targets[0] if targets else None
            if target:
                log.append(skill.apply(actor, target, self._state))
        else:
            # all_enemies / all_allies / self
            for t in targets:
                if t.is_alive():
                    log.append(skill.apply(actor, t, self._state))

    # --- AI: automatische unit kiest actie ---

    def _resolve_unit(self, unit: Unit, log: list[str]) -> None:
        """AI-beslissing voor allies en enemies."""
        is_ally = unit in self.team

        # Probeer eerst een bruikbare skill of spell
        usable = unit.usable_skills(self._state) + unit.usable_spells(self._state)
        if usable:
            skill = usable[0]   # simpele prioriteit: eerste bruikbare
            if skill.target in ("single_enemy", "all_enemies"):
                targets = ([self._get_target(self.enemies)] if is_ally
                           else [self._get_target(self.team)])
                targets = [t for t in targets if t]
            elif skill.target in ("single_ally", "all_allies"):
                pool    = self.team if is_ally else self.enemies
                targets = [min([u for u in pool if u.is_alive()], key=lambda u: u.hp,
                               default=None)]
                targets = [t for t in targets if t]
            else:
                targets = [unit]

            if targets:
                self._resolve_skill(unit, skill, targets, log)
                return

        # Fallback: standaard aanval of heal
        if is_ally:
            if unit.wisdom > unit.attack:
                heal_target = min([u for u in self.team if u.is_alive()],
                                  key=lambda u: u.hp, default=None)
                if heal_target:
                    healed = heal_target.heal(unit.wisdom)
                    log.append(f"{unit.name} heals {heal_target.name} "
                               f"for {healed} HP!")
            else:
                atk_target = self._get_target(self.enemies)
                if atk_target:
                    dmg = atk_target.take_damage(unit.attack)
                    log.append(f"{unit.name} hits {atk_target.name} "
                               f"for {dmg} dmg!")
        else:
            atk_target = self._get_target(self.team)
            if atk_target:
                dmg = atk_target.take_damage(unit.attack)
                log.append(f"{unit.name} hits {atk_target.name} for {dmg} dmg!")
                if not atk_target.is_alive():
                    log.append(f"  >> {atk_target.name} defeated!")

    # --- Player action ---

    def player_action(self, actor: Unit, action: str,
                      target: Unit = None, skill=None) -> str:
        if action == "Attack":
            if target is None:
                target = self._get_target(self.enemies)
            if target is None:
                return "No enemies left."
            dmg = target.take_damage(actor.attack)
            return (f"{actor.name} hits {target.name} for {dmg} dmg! "
                    f"({target.hp}/{target.max_hp} HP)")

        elif action == "Skill" or action == "Spell":
            if skill is None:
                return "No skill selected."
            log = []
            # Bepaal targets op basis van skill.target
            if skill.target == "single_enemy":
                targets = [target] if target else [self._get_target(self.enemies)]
            elif skill.target == "single_ally":
                targets = [target] if target else [self._get_target(self.team)]
            elif skill.target == "all_enemies":
                targets = [e for e in self.enemies if e.is_alive()]
            elif skill.target == "all_allies":
                targets = [u for u in self.team if u.is_alive()]
            else:
                targets = [actor]
            targets = [t for t in targets if t]
            self._resolve_skill(actor, skill, targets, log)
            return " | ".join(log) if log else f"{actor.name} uses {skill.name}."

        elif action == "Defend":
            return f"{actor.name} takes a defensive stance."

        elif action == "Wait":
            return f"{actor.name} waits."

        return f"Unknown action: {action}"

    # --- Volledige ronde ---

    def resolve_turn(self, player_unit: Unit, player_action_name: str,
                     target: Unit = None, skill=None) -> list[str]:
        log        = []
        turn_order = self._get_turn_order()

        for unit in turn_order:
            if not unit.is_alive():
                continue
            if unit == player_unit:
                msg = self.player_action(unit, player_action_name,
                                         target=target, skill=skill)
                log.append(msg)
            else:
                self._resolve_unit(unit, log)
            self._check_defeats(log)

        return log

    def resolve_other_turns(self, player_unit: Unit) -> list[str]:
        """Ronde zonder player action — na item gebruik."""
        log        = []
        turn_order = self._get_turn_order()

        for unit in turn_order:
            if not unit.is_alive() or unit == player_unit:
                continue
            self._resolve_unit(unit, log)
            self._check_defeats(log)

        return log

    def is_over(self) -> bool:
        return (not self._team_alive(self.team) or
                not self._team_alive(self.enemies))

    def outcome(self) -> str:
        if not self._team_alive(self.enemies): return "victory"
        if not self._team_alive(self.team):    return "defeat"
        return "ongoing"
