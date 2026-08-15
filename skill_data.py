from skill import Skill

# ============================================================
# SPELLS
# ============================================================

Heal = Skill(
    name        = "Heal",
    category    = "spell",
    description = "Restores HP to one ally.",
    target      = "single_ally",
    effect      = "heal",
    value       = 10,
    scaling     = "wisdom",
    mp_cost     = 5,
    learn_source= "level",
)

Fireball = Skill(
    name        = "Fireball",
    category    = "spell",
    description = "Hurls a ball of fire at one enemy.",
    elements    = ["fire"],
    target      = "single_enemy",
    effect      = "damage",
    value       = 14,
    scaling     = "wisdom",
    mp_cost     = 6,
    learn_source= "level",
)

Blizzard = Skill(
    name        = "Blizzard",
    category    = "spell",
    description = "Freezing shards strike one enemy.",
    elements    = ["ice"],
    target      = "single_enemy",
    effect      = "damage",
    value       = 12,
    scaling     = "wisdom",
    mp_cost     = 6,
    learn_source= "level",
)

Thunder = Skill(
    name        = "Thunder",
    category    = "spell",
    description = "A bolt of lightning strikes one enemy.",
    elements    = ["thunder"],
    target      = "single_enemy",
    effect      = "damage",
    value       = 13,
    scaling     = "wisdom",
    mp_cost     = 6,
    learn_source= "level",
)

DarkDrain = Skill(
    name        = "Dark Drain",
    category    = "spell",
    description = "Drains life from one enemy.",
    elements    = ["dark"],
    target      = "single_enemy",
    effect      = "drain",
    value       = 10,
    scaling     = "wisdom",
    mp_cost     = 8,
    learn_source= "level",
)

HolyLight = Skill(
    name        = "Holy Light",
    category    = "spell",
    description = "A burst of light damages all enemies.",
    elements    = ["light"],
    target      = "all_enemies",
    effect      = "damage",
    value       = 8,
    scaling     = "wisdom",
    mp_cost     = 10,
    learn_source= "level",
)

# ============================================================
# SKILLS
# ============================================================

PowerStrike = Skill(
    name        = "Power Strike",
    category    = "skill",
    description = "A heavy blow that deals extra damage.",
    target      = "single_enemy",
    effect      = "damage",
    value       = 6,
    scaling     = "attack",
    mp_cost     = 0,
    hp_cost     = 4,
    learn_source= "level",
)

Provoke = Skill(
    name        = "Provoke",
    category    = "skill",
    description = "Taunts an enemy. (debuff — coming soon)",
    target      = "single_enemy",
    effect      = "debuff",
    value       = 0,
    scaling     = "flat",
    mp_cost     = 0,
    learn_source= "level",
)

BattleCry = Skill(
    name        = "Battle Cry",
    category    = "skill",
    description = "Rallies the party. (buff — coming soon)",
    target      = "all_allies",
    effect      = "buff",
    value       = 0,
    scaling     = "flat",
    mp_cost     = 4,
    learn_source= "quest",
)
