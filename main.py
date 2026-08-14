from scene_manager import SceneManager
from title_scene import TitleScene
import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 800))
clock = pygame.time.Clock()

manager = SceneManager()
manager.set_scene(TitleScene())

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.handle_event(event)

    manager.update()
    screen.fill((0, 0, 0))
    manager.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()