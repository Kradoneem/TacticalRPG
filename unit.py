from equipment import Equipment


class Unit:
    """
    Represents a single combat unit (hero, enemy, or boss).
    All combatants in the game inherit from or are instances of this class.
    """

    def __init__(self, name: str, level: int, hp: int, mp: int, attack: int,
                 defense: int, speed: int, wisdom: int, exp: int = 0):
        self.name      = name
        self.level     = level
        self.max_hp    = hp
        self.hp        = hp
        self.max_mp    = mp
        self.mp        = mp
        self.attack    = attack
        self.defense   = defense
        self.speed     = speed
        self.wisdom    = wisdom
        self.equipment = {}
        self.exp       = exp

    def is_alive(self) -> bool:
        return self.hp > 0

    def gain_xp(self, amount: int) -> bool:
        self.exp += amount
        return self.exp >= self.level * 100

    def levelup(self):
        self.exp     -= self.level * 100
        self.level   += 1
        self.attack  += 1
        self.defense += 1
        self.speed   += 1
        self.wisdom  += 1
        self.max_hp  += 5
        self.max_mp  += 2
        return self.level

    def take_damage(self, amount: int) -> int:
        """Applies damage after defense reduction. Returns actual damage dealt."""
        actual = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        """Restores HP up to max_hp. Returns actual amount healed."""
        old_hp  = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def restore_mp(self, amount: int) -> int:
        """Restores MP up to max_mp. Returns actual amount restored."""
        old_mp  = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old_mp

    def spend_mp(self, amount: int) -> bool:
        """Spends MP if available. Returns True on success, False if not enough MP."""
        if self.mp < amount:
            return False
        self.mp -= amount
        return True

    def equip(self, item: Equipment) -> None:
        if item.slot in self.equipment:
            self.unequip(item.slot)
        self.equipment[item.slot] = item
        self.attack  += item.attack
        self.defense += item.defense
        self.speed   += item.speed
        self.wisdom  += item.wisdom
        self.max_hp  += item.hp
        self.hp      += item.hp

    def unequip(self, slot: str) -> None:
        if slot not in self.equipment:
            return
        item = self.equipment.pop(slot)
        self.attack  -= item.attack
        self.defense -= item.defense
        self.speed   -= item.speed
        self.wisdom  -= item.wisdom
        self.max_hp  -= item.hp
        self.hp       = min(self.hp, self.max_hp)

    def __repr__(self) -> str:
        return (f"[{self.name} | Lv.{self.level} | "
                f"HP: {self.hp}/{self.max_hp} | MP: {self.mp}/{self.max_mp} | "
                f"ATK: {self.attack} DEF: {self.defense} "
                f"SPD: {self.speed} WIS: {self.wisdom} "
                f"EXP: {self.exp}/{self.level * 100}]")
