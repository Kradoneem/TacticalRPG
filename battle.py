from unit import Unit


class Battle:
    """
    Manages a tactical battle between two teams.
    Turn order is determined by speed (highest goes first).
    """

    def __init__(self, team: list[Unit], enemies: list[Unit]):
        self.team = team
        self.enemies = enemies
        self._defeated = set()

    def _get_turn_order(self) -> list[Unit]:
        """Returns all living units sorted by speed, highest first."""
        all_units = self.team + self.enemies
        return sorted(all_units, key=lambda u: u.speed, reverse=True)

    def _get_target(self, targets: list[Unit]) -> Unit | None:
        """Returns the living unit with the lowest HP from a given list."""
        living = [u for u in targets if u.is_alive()]
        return min(living, key=lambda u: u.hp) if living else None

    def _team_alive(self, team: list[Unit]) -> bool:
        return any(u.is_alive() for u in team)

    def run(self) -> None:
        print("=== BATTLE START ===\n")
        round_number = 1
        while self._team_alive(self.team) and self._team_alive(self.enemies):
            print(f"--- Round {round_number} ---")
            round_number += 1
            turn_order = self._get_turn_order()

            for unit in turn_order:
                if not unit.is_alive():
                    continue
            
                if unit.wisdom > unit.attack:
                    target = self._get_target(self.team if unit in self.team else self.enemies)
                    if target is None:
                        continue
                    healed = target.heal(unit.wisdom)
                    print(f"{unit.name} heals {target.name} for {healed} HP! "
                        f"({target.hp}/{target.max_hp} HP remaining)")
                else:
                    target = self._get_target(self.enemies if unit in self.team else self.team)
                    if target is None:
                        continue
                    damage = target.take_damage(unit.attack)
                    print(f"{unit.name} hits {target.name} for {damage} damage! "
                        f"({target.hp}/{target.max_hp} HP remaining)")
                    if not target.is_alive():
                        print(f"  >> {target.name} is defeated!")
                        for ally in self.team:
                            if ally.is_alive():
                                # ally.gain_xp(target.hp+target.attack+target.defense+target.speed+target.wisdom)
                                exp = (target.max_hp+target.attack+target.defense+target.speed+target.wisdom)
                                ally.gain_xp(exp)

    def player_action(self, actor: Unit, action: str, target: Unit = None) -> str:
        if action == "Attack":
            if target is None:
                target = self._get_target(self.enemies)
            if target is None:
                return "No enemies left."
            damage = target.take_damage(actor.attack)
            return f"{actor.name} hits {target.name} for {damage} dmg! ({target.hp}/{target.max_hp} HP)"

        elif action == "Heal":
            if target is None:
                target = min(
                    [u for u in self.team if u.is_alive()],
                    key=lambda u: u.hp,
                    default=None
                )
            if target is None:
                return "No allies to heal."
            healed = target.heal(actor.wisdom)
            return f"{actor.name} heals {target.name} for {healed} HP! ({target.hp}/{target.max_hp} HP)"
        
        elif action == "Defend":
            return f"{actor.name} takes a defensive stance."

        elif action == "Wait":
            return f"{actor.name} waits."

        return f"Unknown action: {action}"
    
    def resolve_turn(self, player_unit: Unit, player_action_name: str, target: Unit = None) -> list[str]:
        log = []
        turn_order = self._get_turn_order()

        for unit in turn_order:
            if not unit.is_alive():
                continue

            if unit == player_unit:
                msg = self.player_action(unit, player_action_name, target=target)
                log.append(msg)
            elif unit in self.team:
                # Automatische ally
                if unit.wisdom > unit.attack:
                    target = min([u for u in self.team if u.is_alive()], key=lambda u: u.hp, default=None)
                    if target:
                        healed = target.heal(unit.wisdom)
                        log.append(f"{unit.name} heals {target.name} for {healed} HP!")
                else:
                    target = self._get_target(self.enemies)
                    if target:
                        damage = target.take_damage(unit.attack)
                        log.append(f"{unit.name} hits {target.name} for {damage} dmg!")

            else:
                # Vijand
                target = self._get_target(self.team)
                if target:
                    damage = target.take_damage(unit.attack)
                    log.append(f"{unit.name} hits {target.name} for {damage} dmg!")
                    if not target.is_alive():
                        log.append(f"  >> {target.name} defeated!")
                # --- Na elke actie: check defeats ---
                    for enemy in self.enemies:
                        if not enemy.is_alive() and enemy not in self._defeated:
                            self._defeated.add(enemy)
                            exp = enemy.max_hp + enemy.attack + enemy.defense + enemy.speed + enemy.wisdom
                            log.append(f"  >> {enemy.name} defeated!")
                            for ally in self.team:
                                if ally.is_alive():
                                    leveled = ally.gain_xp(exp)
                                    log.append(f"  >> {ally.name} gains {exp} XP!")
                                    if leveled:
                                        log.append(f"  >> {ally.name} leveled up to {ally.level}!")
        return log

    def is_over(self) -> bool:
        return not self._team_alive(self.team) or not self._team_alive(self.enemies)

    def outcome(self) -> str:
        if not self._team_alive(self.enemies):
            return "victory"
        if not self._team_alive(self.team):
            return "defeat"
        return "ongoing"