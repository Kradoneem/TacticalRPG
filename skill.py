from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unit import Unit
    from game_state import GameState

VALID_ELEMENTS = {"fire", "ice", "thunder", "earth", "dark", "light"}
VALID_TARGETS  = {"single_enemy", "single_ally", "all_enemies", "all_allies", "self"}
VALID_EFFECTS  = {"damage", "heal", "buff", "debuff", "drain"}
VALID_SCALING  = {"attack", "wisdom", "flat"}


class Skill:
    """
    Universele skill/spell klasse.
    category  : "skill" (fysiek/technisch) of "spell" (magisch)
    effect    : wat het doet
    scaling   : waarop de value schaalt ("attack", "wisdom", "flat")
    elements  : lijst van elementen, mag leeg zijn
    item_cost : {"component_type": quantity} — TLR-stijl ingredient cost
    """

    def __init__(
        self,
        name:         str,
        category:     str,
        description:  str        = "",
        elements:     list[str]  = None,
        target:       str        = "single_enemy",
        effect:       str        = "damage",
        value:        int        = 0,
        scaling:      str        = "flat",
        mp_cost:      int        = 0,
        hp_cost:      int        = 0,
        item_cost:    dict       = None,
        learn_source: str        = "level",
    ):
        assert category    in ("skill", "spell"),  f"Ongeldige category: {category}"
        assert target      in VALID_TARGETS,       f"Ongeldig target: {target}"
        assert effect      in VALID_EFFECTS,       f"Ongeldig effect: {effect}"
        assert scaling     in VALID_SCALING,       f"Ongeldige scaling: {scaling}"

        self.name         = name
        self.category     = category
        self.description  = description
        self.elements     = elements or []
        self.target       = target
        self.effect       = effect
        self.value        = value
        self.scaling      = scaling
        self.mp_cost      = mp_cost
        self.hp_cost      = hp_cost
        self.item_cost    = item_cost or {}
        self.learn_source = learn_source

    # --- Resource checks ---

    def can_use(self, unit: Unit, state=None) -> tuple[bool, str]:
        """
        Geeft (True, "") terug als de unit de skill kan gebruiken.
        Geeft (False, reden) terug als dat niet kan.
        """
        if unit.mp < self.mp_cost:
            return False, f"Niet genoeg MP ({self.mp_cost} nodig)"

        if self.hp_cost > 0:
            if unit.hp <= self.hp_cost:
                return False, f"Niet genoeg HP ({self.hp_cost} nodig)"

        if self.item_cost and state:
            for component_type, qty in self.item_cost.items():
                available = sum(
                    1 for item in state.items
                    if getattr(item, "component_type", None) == component_type
                )
                if available < qty:
                    return False, f"Niet genoeg {component_type} ({qty} nodig)"

        return True, ""

    def pay_cost(self, unit: Unit, state=None) -> None:
        """Verbruikt resources. Aanroepen ná can_use check."""
        unit.mp -= self.mp_cost
        unit.hp -= self.hp_cost

        if self.item_cost and state:
            for component_type, qty in self.item_cost.items():
                removed = 0
                for item in list(state.items):
                    if getattr(item, "component_type", None) == component_type and removed < qty:
                        state.items.remove(item)
                        removed += 1

    # --- Effect berekening ---

    def calculate_value(self, actor: Unit) -> int:
        """Berekent de effectieve waarde op basis van scaling."""
        if self.scaling == "attack":
            return self.value + actor.attack
        elif self.scaling == "wisdom":
            return self.value + actor.wisdom
        else:
            return self.value

    def apply(self, actor: Unit, target: Unit, state=None) -> str:
        """
        Past het effect toe op target.
        Geeft een log-string terug.
        Roept pay_cost NIET aan — dat doet de Battle.
        """
        effective = self.calculate_value(actor)

        # Element multiplier op target
        for element in self.elements:
            multiplier = target.element_multipliers.get(element, 1.0)
            effective  = int(effective * multiplier)

        if self.effect == "damage":
            dealt = target.take_damage(effective)
            elem  = f" [{'/'.join(self.elements)}]" if self.elements else ""
            return (f"{actor.name} uses {self.name}{elem} on {target.name} "
                    f"for {dealt} dmg! ({target.hp}/{target.max_hp} HP)")

        elif self.effect == "heal":
            healed = target.heal(effective)
            return (f"{actor.name} uses {self.name} on {target.name}, "
                    f"restoring {healed} HP! ({target.hp}/{target.max_hp} HP)")

        elif self.effect == "drain":
            dealt  = target.take_damage(effective)
            gained = actor.heal(dealt // 2)
            elem   = f" [{'/'.join(self.elements)}]" if self.elements else ""
            return (f"{actor.name} drains {target.name}{elem} "
                    f"for {dealt} dmg, recovers {gained} HP!")

        elif self.effect == "buff":
            return f"{actor.name} uses {self.name} — buff not yet implemented."

        elif self.effect == "debuff":
            return f"{actor.name} uses {self.name} — debuff not yet implemented."

        return f"{actor.name} uses {self.name}."

    def __repr__(self):
        return f"Skill({self.name}, {self.category}, {self.effect})"
