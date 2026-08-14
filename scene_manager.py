import json
import os
from game_state import GameState

SAVE_DIR  = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.state         = GameState()

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

    # --- Save / Load ---

    def save(self) -> bool:
        """
        Schrijft GameState naar saves/save.json.
        Geeft True terug bij succes, False bij fout.
        """
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[Save] Fout: {e}")
            return False

    def load(self) -> bool:
        """
        Laadt GameState uit saves/save.json.
        Geeft True terug bij succes, False als er geen save is of bij fout.
        """
        if not os.path.exists(SAVE_FILE):
            return False
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = GameState.from_dict(data)
            return True
        except Exception as e:
            print(f"[Load] Fout: {e}")
            return False

    def has_save(self) -> bool:
        return os.path.exists(SAVE_FILE)
