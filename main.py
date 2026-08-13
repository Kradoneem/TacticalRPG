from unit import Unit
from equipment import Equipment
from menu import Menu
from battle import Battle
import pygame
import sys

# --- Instellingen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
FPS = 60

# --- Kleuren ---
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (40, 40, 40)
RED    = (255, 0, 0)
DARK_BLUE = (20, 20, 60)
YELLOW    = (255, 220, 0)


def confirm_action(action):
    global active_menu, battle_log
    if action in ["Attack", "Heal"]:
        if action == "Attack":
            target_menu.options = [e for e in battle.enemies if e.is_alive()]
        elif action == "Heal":
            target_menu.options = [u for u in battle.team if u.is_alive()]
        target_menu.selected = 0
        active_menu = target_menu
    else:
        log = battle.resolve_turn(current_unit, action, target=None)
        battle_log.extend(log)
        battle_log = battle_log[-5:]

def confirm_target(target):
    global active_menu, battle_log
    log = battle.resolve_turn(current_unit, action_menu.current, target=target)
    battle_log.extend(log)
    battle_log = battle_log[-5:]
    active_menu = action_menu

def cancel_target():
    global active_menu
    active_menu = action_menu

def is_targeted(unit):
    return (
        active_menu == target_menu and
        unit in target_menu.options and
        target_menu.options.index(unit) == target_menu.selected
    )

def draw_menu(surface, font, options, selected):
    menu_x = 80
    menu_y = 740
    for i, option in enumerate(options):
        color = YELLOW if i == selected else WHITE
        text = font.render(f"[{i+1}] {option}", True, color)
        surface.blit(text, (menu_x + i * 200, menu_y))

def draw_unit(surface, font, name, hp, max_hp, x, y, color, selected=False):
    # Blok
    pygame.draw.rect(surface, color, (x, y, 160, 80))
    if selected:
        pygame.draw.rect(surface, YELLOW, (x, y, 160, 80), 3)
    # Naam
    name_text = font.render(name, True, WHITE)
    surface.blit(name_text, (x + 8, y + 8))
    # HP tekst
    hp_text = font.render(f"HP: {hp}/{max_hp}", True, WHITE)
    surface.blit(hp_text, (x + 8, y + 30))
    # HP balk
    bar_width = 144
    filled = int(bar_width * (hp / max_hp))
    if (hp / max_hp) < 0.5:
        hp_bar = 200, 0, 0
    else:
        hp_bar = 0, 200, 0
    pygame.draw.rect(surface, BLACK, (x + 8, y + 55, bar_width, 12))
    pygame.draw.rect(surface, hp_bar, (x + 8, y + 55, filled, 12))

def draw_log(surface, font, log):
    log_x = 80
    log_y = 530
    for i, line in enumerate(log):
        text = font.render(line, True, WHITE)
        surface.blit(text, (log_x, log_y + i * 22))

def init_battle():
    global hero, companion, goblin, orc, battle, battle_log, battle_over, battle_outcome, current_unit, active_menu

    hero      = Unit("Nemo",   level=1, hp=40, attack=12, defense=4, speed=8,  wisdom=5)
    companion = Unit("Jeerus", level=1, hp=20, attack=5,  defense=5, speed=6,  wisdom=15)
    goblin    = Unit("Goblin", level=1, hp=20, attack=8,  defense=2, speed=5,  wisdom=2)
    orc       = Unit("Orc",    level=2, hp=35, attack=10, defense=4, speed=3,  wisdom=1)

    battle         = Battle(team=[hero, companion], enemies=[goblin, orc])
    current_unit   = hero
    battle_log     = []
    battle_over    = False
    battle_outcome = ""
    active_menu    = action_menu
    action_menu.selected = 0


# --- Init ---
pygame.init()
font = pygame.font.SysFont("monospace", 16)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TacticalRPG — Battle")
clock = pygame.time.Clock()

actions = ["Attack", "Heal", "Defend", "Wait"]
selected_action = 0
action_menu = Menu(options=actions, on_confirm=confirm_action)
target_menu = Menu(options=[], on_confirm=confirm_target, on_cancel=cancel_target)

init_battle()

# --- Game loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if battle_over:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    init_battle()
                continue  # blokkeer alle andere input als battle voorbij is
            if event.key == pygame.K_ESCAPE:
                running = False
            else:
                 active_menu.handle_key(event.key)

    screen.fill(BLACK)
    if battle.is_over() and not battle_over:
        battle_over = True
        battle_outcome = battle.outcome()

    enemy_positions = [(80, 80), (260, 80), (440, 80), (620, 80)]
    ally_positions  = [(80, 640), (260, 640), (440, 640), (620, 640)]

    enemy_units = list(zip(battle.enemies, enemy_positions))
    ally_units  = list(zip(battle.team, ally_positions))
    

    # draw_unit(screen, font, hero.name, hero.hp, hero.max_hp, x=80,  y=640, color=(30, 80, 160))
    # draw_unit(screen, font, companion.name, companion.hp, companion.max_hp, x=260, y=640, color=(30, 80, 160))
    # draw_unit(screen, font, goblin.name, goblin.hp, goblin.max_hp, x=80, y=80, color=(160, 40, 40))
    # draw_unit(screen, font, orc.name, orc.hp, orc.max_hp, x=260, y=80, color=(160, 40, 40))
    for unit, (x, y) in enemy_units:
        draw_unit(screen, font, unit.name, unit.hp, unit.max_hp, x=x, y=y,
                color=(160, 40, 40), selected=is_targeted(unit))

    for unit, (x, y) in ally_units:
        draw_unit(screen, font, unit.name, unit.hp, unit.max_hp, x=x, y=y,
                color=(30, 80, 160), selected=is_targeted(unit))
    draw_menu(screen, font, 
          [u.name for u in active_menu.options] if active_menu == target_menu else active_menu.options,
          active_menu.selected)
    draw_log(screen, font, battle_log)

    if battle_over:
        if battle_outcome == "victory":
            msg = "VICTORY!"
            color = YELLOW
        else:
            msg = "DEFEAT..."
            color = RED
        text = font.render(msg, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        restart_text = font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()