import os
import pygame

from engine.core.engineconfig import RESOURCEPATHS


class SoundManager:
    def __init__(
            self,
            ctx,
            freq=22050,
            size=-16,
            channels=2,
            buffer=512,
            volume=1.0,
    ):
        """
        freq     22050 = retro / NES-ish
        size     -16   = signed 16-bit
        channels 2     = stereo
        buffer   512   = low latency
        """
        self.ctx = ctx
        pygame.mixer.pre_init(freq, size, channels, buffer)
        pygame.mixer.init()

        self.base_path = RESOURCEPATHS['sound']
        self.volume = volume
        self.sounds = {}

        self._load_all()

    # -------------------------------------------------

    def _load_all(self):
        supported = (".wav", ".ogg", ".mp3")

        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith(supported):
                    full = os.path.join(root, file)
                    key = os.path.relpath(full, self.base_path).replace("\\", "/")

                    sound = pygame.mixer.Sound(full)
                    sound.set_volume(self.volume)
                    self.sounds[key] = sound
                    print(f"[SoundManager] Loaded sound: {key}")

        print(f"[SoundManager] Loaded {len(self.sounds)} sounds")

    # -------------------------------------------------

    def play(self, name):
        if name not in self.sounds:
            raise KeyError(f"Sound not found: {name}")
        self.sounds[name].play()

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def stop_all(self):
        pygame.mixer.stop()

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        for s in self.sounds.values():
            s.set_volume(self.volume)

    def list(self):
        return sorted(self.sounds.keys())
