from unit import Unit
from equipment import Equipment


class GameState:
    """
    Central game state. Lives in SceneManager.
    All scenes read from and write to this object.
    Supports serialisation to/from dict for save/load.
    """

    def __init__(self):
        self.party     = self._default_party()
        self.inventory = self._default_inventory()

    # --- Defaults ---

    def _default_party(self) -> list:
        return [
            Unit(name="Nemo",   level=1, hp=40, attack=12, defense=4, speed=8,  wisdom=5),
            Unit(name="Jeerus", level=1, hp=20, attack=5,  defense=5, speed=6,  wisdom=15),
        ]

    def _default_inventory(self) -> list:
        return [
            Equipment(name="Iron Sword",      slot="weapon",    attack=5),
            Equipment(name="Wooden Shield",    slot="armor",     defense=3, hp=5),
            Equipment(name="Berserker's Ring", slot="accessory", attack=4),
            Equipment(name="Sage's Ring",      slot="accessory", wisdom=4),
        ]

    # --- Serialisatie ---

    def to_dict(self) -> dict:
        return {
            "party":     [self._unit_to_dict(u) for u in self.party],
            "inventory": [item.to_dict() for item in self.inventory],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state = cls.__new__(cls)   # __init__ overslaan
        state.party     = [cls._unit_from_dict(u) for u in data["party"]]
        state.inventory = [Equipment.from_dict(i) for i in data["inventory"]]
        return state

    # --- Unit serialisatie ---
    # Unit heeft geen eigen to_dict — we doen het hier zodat unit.py clean blijft.
    # Als Unit later subclasses krijgt, verhuist dit naar Unit zelf.

    @staticmethod
    def _unit_to_dict(unit: Unit) -> dict:
        return {
            "name":      unit.name,
            "level":     unit.level,
            "hp":        unit.hp,
            "max_hp":    unit.max_hp,
            "attack":    unit.attack,
            "defense":   unit.defense,
            "speed":     unit.speed,
            "wisdom":    unit.wisdom,
            "exp":       unit.exp,
            "equipment": {
                slot: item.to_dict()
                for slot, item in unit.equipment.items()
            },
        }

    @staticmethod
    def _unit_from_dict(data: dict) -> Unit:
        unit = Unit(
            name    = data["name"],
            level   = data["level"],
            hp      = data["max_hp"],   # Unit.__init__ zet max_hp = hp
            attack  = data["attack"],
            defense = data["defense"],
            speed   = data["speed"],
            wisdom  = data["wisdom"],
            exp     = data.get("exp", 0),
        )
        unit.hp = data["hp"]            # huidige HP apart terugzetten

        for slot, item_data in data.get("equipment", {}).items():
            item = Equipment.from_dict(item_data)
            unit.equipment[slot] = item  # direct in dict — geen stat-bonus dubbeltelling

        return unit
