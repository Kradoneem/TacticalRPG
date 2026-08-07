class Unit:
    """
    Represents a single combat unit (hero, enemy, or boss).
    All combatants in the game inherit from or are instances of this class.
    """

    def __init__(self, name: str, level: int, hp: int, attack: int, defense: int, speed: int):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        """
        Applies damage after defense reduction.
        Returns the actual damage dealt.
        """
        actual_damage = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def __repr__(self) -> str:
        return (f"[{self.name} | Lv.{self.level} | "
                f"HP: {self.hp}/{self.max_hp} | "
                f"ATK: {self.attack} DEF: {self.defense} SPD: {self.speed}]")


# --- Test ---
if __name__ == "__main__":
    hero = Unit(name="Kael", level=1, hp=40, attack=12, defense=4, speed=8)
    enemy = Unit(name="Goblin Scout", level=1, hp=20, attack=8, defense=2, speed=5)

    print(hero)
    print(enemy)

    damage = enemy.take_damage(hero.attack)
    print(f"\n{hero.name} hits {enemy.name} for {damage} damage!")
    print(enemy)
    print(f"{enemy.name} alive: {enemy.is_alive()}")
