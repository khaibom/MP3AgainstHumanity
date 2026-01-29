import os
import time
import pygame

MUSIC_DIR = "./songs"

SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg")

def get_songs(directory):
    return [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

def main():
    songs = get_songs(MUSIC_DIR)

    if not songs:
        print("No audio files found.")
        return

    pygame.mixer.init()
    print(f"Found {len(songs)} songs. Starting playback...\n")

    for song in songs:
        print(f"Playing: {os.path.basename(song)}")
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

        # Wait until song finishes
        while pygame.mixer.music.get_busy():
            time.sleep(1)

    print("\nPlaylist finished!")

if __name__ == "__main__":
    main()