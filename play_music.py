import os
import time
import random
import pygame

MUSIC_DIR = "./songs"
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg")

def get_songs(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]

def choose_mode():
    print("Choose playback mode:")
    print("1️⃣  Sequential (safe, predictable)")
    print("2️⃣  Random (train chaos)")
    choice = input("Enter 1 or 2: ").strip()

    return choice

def main():
    songs = get_songs(MUSIC_DIR)

    if not songs:
        print("❌ No audio files found.")
        return

    mode = choose_mode()

    if mode == "2":
        random.shuffle(songs)
        print("\n🔀 Random mode activated.\n")
    else:
        print("\n▶️ Sequential mode activated.\n")

    pygame.mixer.init()
    print(f"Found {len(songs)} songs. Starting playback...\n")

    for song in songs:
        print(f"🎵 Playing: {os.path.basename(song)}")
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(1)

    print("\n🎧 Playlist finished!")

if __name__ == "__main__":
    main()