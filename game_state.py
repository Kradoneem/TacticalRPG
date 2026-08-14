from unit import Unit
from equipment import Equipment


class GameState:
    """
    Central game state. Lives in SceneManager.
    All scenes read from and write to this object.
    """

    def __init__(self):
        self.party     = self._default_party()
        self.inventory = self._default_inventory()

    def _default_party(self) -> list:
        return [
            Unit(name="Nemo",   level=1, hp=40, attack=12, defense=4, speed=8,  wisdom=5),
            Unit(name="Jeerus", level=1, hp=20, attack=5,  defense=5, speed=6,  wisdom=15),
        ]

    def _default_inventory(self) -> list:
        return [
            Equipment(name="Iron Sword",       slot="weapon",    attack=5),
            Equipment(name="Wooden Shield",     slot="armor",     defense=3, hp=5),
            Equipment(name="Berserker's Ring",  slot="accessory", attack=4),
            Equipment(name="Sage's Ring",       slot="accessory", wisdom=4),
        ]
