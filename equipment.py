class Equipment:
    """
    Represents a single piece of equipment (weapon, armor, or accessory).
    Stat bonuses are added to a Unit when equipped.
    """

    VALID_SLOTS = ("weapon", "armor", "accessory")

    def __init__(self, name: str, slot: str, attack: int = 0, defense: int = 0,
                 speed: int = 0, wisdom: int = 0, hp: int = 0):
        if slot not in self.VALID_SLOTS:
            raise ValueError(f"Invalid slot '{slot}'. Choose from: {self.VALID_SLOTS}")
        self.name    = name
        self.slot    = slot
        self.attack  = attack
        self.defense = defense
        self.speed   = speed
        self.wisdom  = wisdom
        self.hp      = hp

    def __repr__(self) -> str:
        bonuses = []
        for stat in ("attack", "defense", "speed", "wisdom", "hp"):
            value = getattr(self, stat)
            if value != 0:
                bonuses.append(f"{stat.upper()}+{value}")
        return f"[{self.name} | {self.slot} | {', '.join(bonuses)}]"

    def to_dict(self) -> dict:
        return {
            "name":    self.name,
            "slot":    self.slot,
            "attack":  self.attack,
            "defense": self.defense,
            "speed":   self.speed,
            "wisdom":  self.wisdom,
            "hp":      self.hp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Equipment":
        return cls(
            name    = data["name"],
            slot    = data["slot"],
            attack  = data.get("attack",  0),
            defense = data.get("defense", 0),
            speed   = data.get("speed",   0),
            wisdom  = data.get("wisdom",  0),
            hp      = data.get("hp",      0),
        )
