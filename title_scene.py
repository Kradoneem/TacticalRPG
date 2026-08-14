import pygame

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
YELLOW = (255, 220, 0)

class TitleScene:
    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 32)
        self.small_font = pygame.font.SysFont("monospace", 16)

    def handle_event(self, event, manager):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                print("start battle")
                from battle_scene import BattleScene
                manager.set_scene(BattleScene())

    def update(self, manager):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title = self.font.render("TacticalRPG", True, YELLOW)
        prompt = self.small_font.render("Press ENTER to start", True, WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 300))
        screen.blit(prompt, (screen.get_width() // 2 - prompt.get_width() // 2, 380))