import json
import os
import pygame
from game_state import GameState
from party_menu import PartyMenu

SAVE_DIR  = "saves"
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.state         = GameState()
        self.party_menu    = PartyMenu()

    def set_scene(self, scene):
        self.current_scene = scene
        # Reset de on_item_used callback bij elke scène-wissel
        self.party_menu.on_item_used = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            if self.current_scene:
                self.current_scene.handle_event(event, self)
            return

        # M of TAB opent/sluit het party menu
        if event.key in (pygame.K_m, pygame.K_TAB):
            self.party_menu.toggle()
            return

        # Als menu open is: input gaat naar het menu
        if self.party_menu.open:
            self.party_menu.handle_key(event.key, self.state, self)
            return

        # Anders naar de actieve scene
        if self.current_scene:
            self.current_scene.handle_event(event, self)

    def update(self):
        if self.current_scene:
            self.current_scene.update(self)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)
        # Party menu altijd bovenop tekenen
        self.party_menu.draw(screen, self.state)

    # --- Save / Load ---

    def save(self) -> bool:
        try:
            os.makedirs(SAVE_DIR, exist_ok=True)
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.state.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[Save] Fout: {e}")
            return False

    def load(self) -> bool:
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
