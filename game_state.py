from unit import Unit
from equipment import Equipment
from item import Item
import skill_data


class GameState:
    """
    Central game state. Lives in SceneManager.
    All scenes read from and write to this object.
    Supports serialisation to/from dict for save/load.
    """

    def __init__(self):
        self.party     = self._default_party()
        self.equipment = self._default_equipment()
        self.items     = self._default_items()

    # --- Defaults ---

    def _default_party(self) -> list:
        nemo = Unit(name="Nemo", level=1, hp=40, attack=12,
                    defense=4, speed=8, wisdom=5, mp=0)
        nemo.learn(skill_data.PowerStrike)

        jeerus = Unit(name="Jeerus", level=1, hp=20, attack=5,
                      defense=5, speed=6, wisdom=15, mp=50)
        jeerus.learn(skill_data.Heal)
        jeerus.learn(skill_data.Fireball)

        return [nemo, jeerus]

    def _default_equipment(self) -> list:
        return [
            Equipment(name="Iron Sword",      slot="weapon",    attack=5),
            Equipment(name="Wooden Shield",    slot="armor",     defense=3, hp=5),
            Equipment(name="Berserker's Ring", slot="accessory", attack=4),
            Equipment(name="Sage's Ring",      slot="accessory", wisdom=4),
        ]

    def _default_items(self) -> list:
        return [
            Item(name="Potion",       effect="heal_hp",  value=20, target="single",
                 description="Restores 20 HP to one ally."),
            Item(name="Hi-Potion",    effect="heal_hp",  value=50, target="single",
                 description="Restores 50 HP to one ally."),
            Item(name="Ether",        effect="heal_mp",  value=10, target="single",
                 description="Restores 10 MP to one ally."),
            Item(name="Elixir",       effect="heal_all", value=30, target="single",
                 description="Restores 30 HP and MP to one ally."),
            Item(name="Group Potion", effect="heal_hp",  value=15, target="all",
                 description="Restores 15 HP to all allies."),
        ]

    # --- Serialisatie ---

    def to_dict(self) -> dict:
        return {
            "party":     [self._unit_to_dict(u) for u in self.party],
            "equipment": [e.to_dict() for e in self.equipment],
            "items":     [i.to_dict() for i in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state           = cls.__new__(cls)
        state.party     = [cls._unit_from_dict(u) for u in data["party"]]
        state.equipment = [Equipment.from_dict(e) for e in data.get("equipment", [])]
        state.items     = [Item.from_dict(i) for i in data.get("items", [])]
        return state

    # --- Unit serialisatie ---
    # Opmerking: learned skills/spells worden niet geserialiseerd —
    # ze worden bij from_dict opnieuw toegekend op basis van naam.
    # Dit voorkomt complexe skill-serialisatie zolang er geen class-systeem is.

    @staticmethod
    def _unit_to_dict(unit: Unit) -> dict:
        return {
            "name":          unit.name,
            "level":         unit.level,
            "hp":            unit.hp,
            "max_hp":        unit.max_hp,
            "mp":            unit.mp,
            "max_mp":        unit.max_mp,
            "attack":        unit.attack,
            "defense":       unit.defense,
            "speed":         unit.speed,
            "wisdom":        unit.wisdom,
            "exp":           unit.exp,
            "equipment":     {
                slot: item.to_dict()
                for slot, item in unit.equipment.items()
            },
            "learned_skills": [s.name for s in unit.learned_skills],
            "learned_spells": [s.name for s in unit.learned_spells],
        }

    @staticmethod
    def _unit_from_dict(data: dict) -> Unit:
        unit = Unit(
            name    = data["name"],
            level   = data["level"],
            hp      = data["max_hp"],
            attack  = data["attack"],
            defense = data["defense"],
            speed   = data["speed"],
            wisdom  = data["wisdom"],
            mp      = data.get("max_mp", 0),
            exp     = data.get("exp", 0),
        )
        unit.hp = data["hp"]
        unit.mp = data.get("mp", unit.max_mp)

        for slot, item_data in data.get("equipment", {}).items():
            item = Equipment.from_dict(item_data)
            unit.equipment[slot] = item   # direct — geen dubbele stat-bonus

        # Skills en spells herstellen op naam
        skill_lookup = {s.name: s for s in vars(skill_data).values()
                        if hasattr(s, "category")}
        for name in data.get("learned_skills", []):
            if name in skill_lookup:
                unit.learn(skill_lookup[name])
        for name in data.get("learned_spells", []):
            if name in skill_lookup:
                unit.learn(skill_lookup[name])

        return unit
