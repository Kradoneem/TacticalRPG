from game_state import GameState

class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.state         = GameState()   # gedeelde game state voor alle scenes

    def set_scene(self, scene):
        self.current_scene = scene

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event, self)

    def update(self):
        if self.current_scene:
            self.current_scene.update(self)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)
