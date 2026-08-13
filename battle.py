from unit import Unit


class Battle:
    """
    Manages a tactical battle between two teams.
    Turn order is determined by speed (highest goes first).
    """

    def __init__(self, team: list[Unit], enemies: list[Unit]):
        self.team = team
        self.enemies = enemies

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


# --- Test ---
if __name__ == "__main__":
    from equipment import Equipment

    hero = Unit(name="Nemo", level=1, hp=40, attack=12, defense=4, speed=8, wisdom=5)
    companion = Unit(name="Jeerus", level=1, hp=20, attack=5, defense=5, speed=6, wisdom=15)

    sword = Equipment(name="Iron Sword", slot="weapon", attack=5)
    hero.equip(sword)
    ring = Equipment(name="Sage's Ring", slot="accessory", wisdom=5)
    companion.equip(ring)



    goblin = Unit(name="Goblin Scout", level=1, hp=30, attack=8, defense=2, speed=5, wisdom=2, exp=0)
    orc = Unit(name="Orc Grunt", level=2, hp=55, attack=10, defense=5, speed=3, wisdom=1, exp=0)

    battle = Battle(team=[hero, companion], enemies=[goblin, orc])
    battle.run()