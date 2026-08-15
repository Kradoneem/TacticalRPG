class Item:
    """
    Consumable item that applies an effect to a Unit.

    Effects:
        heal_hp   — restores HP by value
        heal_mp   — restores MP by value
        heal_all  — restores both HP and MP by value

    Target:
        single    — used on one unit
        all       — used on entire party
    """

    VALID_EFFECTS = ("heal_hp", "heal_mp", "heal_all")
    VALID_TARGETS = ("single", "all")

    def __init__(self, name: str, effect: str, value: int, target: str = "single",
                 description: str = ""):
        if effect not in self.VALID_EFFECTS:
            raise ValueError(f"Invalid effect '{effect}'. Choose from: {self.VALID_EFFECTS}")
        if target not in self.VALID_TARGETS:
            raise ValueError(f"Invalid target '{target}'. Choose from: {self.VALID_TARGETS}")

        self.name        = name
        self.effect      = effect
        self.value       = value
        self.target      = target
        self.description = description

    def use_on(self, unit) -> str:
        """
        Applies effect to a single Unit.
        Returns a log string describing what happened.
        """
        if self.effect == "heal_hp":
            restored = unit.heal(self.value)
            return f"{unit.name} recovers {restored} HP."

        elif self.effect == "heal_mp":
            restored = unit.restore_mp(self.value)
            return f"{unit.name} recovers {restored} MP."

        elif self.effect == "heal_all":
            hp_restored = unit.heal(self.value)
            mp_restored = unit.restore_mp(self.value)
            return f"{unit.name} recovers {hp_restored} HP and {mp_restored} MP."

        return ""

    def to_dict(self) -> dict:
        return {
            "name":        self.name,
            "effect":      self.effect,
            "value":       self.value,
            "target":      self.target,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            name        = data["name"],
            effect      = data["effect"],
            value       = data["value"],
            target      = data.get("target", "single"),
            description = data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"[{self.name} | {self.effect} +{self.value} | {self.target}]"
