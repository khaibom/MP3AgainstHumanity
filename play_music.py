import os
import time
import random
import difflib
import pygame

MUSIC_DIR = "./songs"
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg")
WINDOW_SIZE = (820, 520)
MAX_RESULTS = 6
PROGRESS_BAR_HEIGHT = 12


def get_songs(directory):
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]


def normalize_title(path):
    return os.path.splitext(os.path.basename(path))[0]


class Player:
    def __init__(self, songs):
        self.songs = songs
        self.index = 0
        self.is_paused = False
        self.last_start_time = 0.0
        self.play_start_time = 0.0
        self.seek_position = 0.0
        self.pause_started = None
        self.track_length = 0.0

    def has_songs(self):
        return bool(self.songs)

    def current_path(self):
        if not self.songs:
            return None
        return self.songs[self.index]

    def current_title(self):
        path = self.current_path()
        return normalize_title(path) if path else "No track"

    def play_index(self, index):
        if not self.songs:
            return
        self.index = index % len(self.songs)
        self.play()

    def play(self):
        path = self.current_path()
        if not path:
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.is_paused = False
        self.last_start_time = time.time()
        self.play_start_time = time.time()
        self.seek_position = 0.0
        self.pause_started = None
        self.track_length = self._load_track_length(path)

    def toggle_pause(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            if self.pause_started is not None:
                self.play_start_time += time.time() - self.pause_started
                self.pause_started = None
        else:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.pause_started = time.time()

    def next_track(self):
        if not self.songs:
            return
        self.index = (self.index + 1) % len(self.songs)
        self.play()

    def prev_track(self):
        if not self.songs:
            return
        self.index = (self.index - 1) % len(self.songs)
        self.play()

    def _load_track_length(self, path):
        try:
            return pygame.mixer.Sound(path).get_length()
        except pygame.error:
            return 0.0

    def current_position(self):
        if not self.songs or self.play_start_time == 0.0:
            return 0.0
        if self.pause_started is not None:
            elapsed = self.pause_started - self.play_start_time
        else:
            elapsed = time.time() - self.play_start_time
        return max(0.0, self.seek_position + elapsed)

    def seek(self, position):
        if not self.songs or self.track_length <= 0:
            return
        position = max(0.0, min(position, self.track_length - 0.05))
        try:
            pygame.mixer.music.play(start=position)
            self.is_paused = False
            self.last_start_time = time.time()
            self.play_start_time = time.time()
            self.seek_position = position
            self.pause_started = None
        except pygame.error:
            self.play()

    def update(self):
        if not self.songs or self.is_paused:
            return
        if not pygame.mixer.music.get_busy():
            if time.time() - self.last_start_time > 0.5:
                self.next_track()


def build_search_results(titles, query):
    if not query:
        return list(range(min(len(titles), MAX_RESULTS)))

    query_lower = query.lower()
    substring_matches = [
        i for i, title in enumerate(titles) if query_lower in title.lower()
    ]
    close_matches = difflib.get_close_matches(
        query, titles, n=MAX_RESULTS, cutoff=0.2
    )
    close_indices = [
        titles.index(title) for title in close_matches if title in titles
    ]

    ordered = []
    for idx in substring_matches + close_indices:
        if idx not in ordered:
            ordered.append(idx)

    return ordered[:MAX_RESULTS]


def draw_button(surface, rect, label, font, is_hovered=False):
    base_color = (40, 40, 40)
    hover_color = (70, 70, 70)
    text_color = (230, 230, 230)
    pygame.draw.rect(surface, hover_color if is_hovered else base_color, rect, border_radius=6)
    text = font.render(label, True, text_color)
    text_rect = text.get_rect(center=rect.center)
    surface.blit(text, text_rect)


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def main():
    songs = get_songs(MUSIC_DIR)

    if not songs:
        print("❌ No audio files found.")
        return

    # Default to sequential for immediate GUI startup.

    pygame.init()
    pygame.mixer.init()

    player = Player(songs)
    player.play()

    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("MP3AgainstHumanity")
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 28)
    clock = pygame.time.Clock()

    search_text = ""
    song_titles = [normalize_title(path) for path in songs]
    buttons = {
        "prev": pygame.Rect(40, 95, 120, 44),
        "play_pause": pygame.Rect(180, 95, 120, 44),
        "next": pygame.Rect(320, 95, 120, 44),
    }
    progress_rect = pygame.Rect(40, 70, 740, PROGRESS_BAR_HEIGHT)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.toggle_pause()
                elif event.key == pygame.K_RIGHT:
                    player.next_track()
                elif event.key == pygame.K_LEFT:
                    player.prev_track()
                elif event.key == pygame.K_RETURN:
                    results = build_search_results(song_titles, search_text)
                    if results:
                        player.play_index(results[0])
                elif event.key == pygame.K_ESCAPE:
                    search_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    search_text = search_text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        search_text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons["prev"].collidepoint(event.pos):
                    player.prev_track()
                elif buttons["play_pause"].collidepoint(event.pos):
                    player.toggle_pause()
                elif buttons["next"].collidepoint(event.pos):
                    player.next_track()
                elif progress_rect.collidepoint(event.pos):
                    if player.track_length > 0:
                        offset = event.pos[0] - progress_rect.x
                        ratio = max(0.0, min(offset / progress_rect.width, 1.0))
                        player.seek(ratio * player.track_length)
                else:
                    results = build_search_results(song_titles, search_text)
                    start_y = 240
                    for i, idx in enumerate(results):
                        row_rect = pygame.Rect(40, start_y + i * 40, 740, 32)
                        if row_rect.collidepoint(event.pos):
                            player.play_index(idx)
                            break

        player.update()

        screen.fill((18, 18, 18))

        title_text = title_font.render(
            f"Now Playing: {player.current_title()}",
            True,
            (240, 240, 240),
        )
        screen.blit(title_text, (40, 30))

        pygame.draw.rect(screen, (30, 30, 30), progress_rect, border_radius=6)
        if player.track_length > 0:
            progress = player.current_position() / player.track_length
            progress = max(0.0, min(progress, 1.0))
            filled = pygame.Rect(
                progress_rect.x,
                progress_rect.y,
                int(progress_rect.width * progress),
                progress_rect.height,
            )
            pygame.draw.rect(screen, (90, 90, 90), filled, border_radius=6)
            time_label = font.render(
                f"{format_time(player.current_position())} / {format_time(player.track_length)}",
                True,
                (200, 200, 200),
            )
            screen.blit(time_label, (40, 145))

        draw_button(
            screen,
            buttons["prev"],
            "Prev",
            font,
            buttons["prev"].collidepoint(mouse_pos),
        )
        draw_button(
            screen,
            buttons["play_pause"],
            "Pause" if not player.is_paused else "Play",
            font,
            buttons["play_pause"].collidepoint(mouse_pos),
        )
        draw_button(
            screen,
            buttons["next"],
            "Next",
            font,
            buttons["next"].collidepoint(mouse_pos),
        )

        search_label = font.render("Search title:", True, (200, 200, 200))
        screen.blit(search_label, (40, 160))
        pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(40, 185, 740, 34), border_radius=4)
        search_value = font.render(search_text or "Type to search...", True, (230, 230, 230))
        screen.blit(search_value, (50, 192))

        results = build_search_results(song_titles, search_text)
        start_y = 240
        for i, idx in enumerate(results):
            row_rect = pygame.Rect(40, start_y + i * 40, 740, 32)
            pygame.draw.rect(screen, (24, 24, 24), row_rect, border_radius=4)
            label = font.render(song_titles[idx], True, (210, 210, 210))
            screen.blit(label, (50, start_y + i * 40 + 6))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()