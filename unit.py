from __future__ import annotations
from equipment import Equipment


class Unit:
    def __init__(self, name, level, hp, attack, defense, speed, wisdom, mp=0, exp=0):
        self.name    = name
        self.level   = level
        self.max_hp  = hp
        self.hp      = hp
        self.max_mp  = mp
        self.mp      = mp
        self.attack  = attack
        self.defense = defense
        self.speed   = speed
        self.wisdom  = wisdom
        self.exp     = exp
        self.equipment:          dict  = {}
        self.learned_skills:     list  = []
        self.learned_spells:     list  = []
        self.element_multipliers: dict = {}  # {"fire": 1.5, "ice": 0.5}

    def is_alive(self):       return self.hp > 0
    def take_damage(self, amount):
        actual = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual
    def heal(self, amount):
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old
    def gain_xp(self, amount):
        log = []
        self.exp += amount
        log.append(f"  {self.name} gains {amount} XP! ({self.exp}/{self.level * 100})")
        while self.exp >= self.level * 100:
            self.exp -= self.level * 100
            log.extend(self._level_up())
        return log
    def _level_up(self):
        self.level += 1; self.attack += 1; self.defense += 1
        self.speed += 1; self.wisdom += 1; self.max_hp += 5
        self.hp = self.max_hp
        return [f"  * {self.name} reached level {self.level}!", "    ATK+1 DEF+1 SPD+1 WIS+1 MaxHP+5"]
    def learn(self, skill):
        target = self.learned_skills if skill.category == "skill" else self.learned_spells
        if skill not in target: target.append(skill)
    def forget(self, skill):
        for lst in (self.learned_skills, self.learned_spells):
            if skill in lst: lst.remove(skill)
    def usable_skills(self, state=None):
        return [s for s in self.learned_skills if s.can_use(self, state)[0]]
    def usable_spells(self, state=None):
        return [s for s in self.learned_spells if s.can_use(self, state)[0]]
    def equip(self, item):
        if item.slot in self.equipment: self.unequip(item.slot)
        self.equipment[item.slot] = item
        self.attack += item.attack; self.defense += item.defense
        self.speed += item.speed;   self.wisdom += item.wisdom
        self.max_hp += item.hp;     self.hp += item.hp
        if hasattr(item, "grants_skill") and item.grants_skill: self.learn(item.grants_skill)
    def unequip(self, slot):
        if slot not in self.equipment: return
        item = self.equipment.pop(slot)
        self.attack -= item.attack; self.defense -= item.defense
        self.speed -= item.speed;   self.wisdom -= item.wisdom
        self.max_hp -= item.hp;     self.hp = min(self.hp, self.max_hp)
        if hasattr(item, "grants_skill") and item.grants_skill: self.forget(item.grants_skill)
    def __repr__(self):
        return (f"[{self.name} | Lv.{self.level} | HP {self.hp}/{self.max_hp} "
                f"MP {self.mp}/{self.max_mp} | ATK {self.attack} DEF {self.defense} "
                f"SPD {self.speed} WIS {self.wisdom}]")