import csv
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: Optional[str]
    favorite_mood: Optional[str]
    target_energy: Optional[float]
    target_valence: Optional[float]
    target_danceability: Optional[float]
    target_tempo_bpm: Optional[float]
    target_acousticness: Optional[float]

@dataclass
class Recommendation:
    """A recommended song with its score (0 to 1) and reasons, strongest first."""
    song: Song
    score: float
    reasons: List[str]

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    # --- Scoring constants ---------------------------------------------------
    # These describe how the system scores, not a song or a user.

    # Mood, energy and valence are the strongest signals. Tempo and acousticness
    # mostly duplicate energy in this dataset, so they stay low.
    WEIGHTS = {
        "mood": 2.0,
        "energy": 2.0,
        "valence": 2.0,
        "genre": 1.0,
        "danceability": 0.75,
        "tempo": 0.25,
        "acousticness": 0.25,
    }

    # Tolerance for Gaussian closeness: a gap of one sigma scores ~0.61, two
    # sigmas ~0.14. Tempo's sigma is in BPM, so tempo needs no normalizing.
    SIGMAS = {
        "energy": 0.15,
        "valence": 0.15,
        "danceability": 0.15,
        "acousticness": 0.15,
        "tempo": 15.0,
    }

    # Moods in the same family earn partial credit instead of a hard 0.
    MOOD_FAMILIES = [
        {"chill", "relaxed", "focused", "peaceful"},
        {"happy", "carefree", "euphoric", "energetic", "confident"},
        {"intense", "angry"},
        {"sad", "melancholic", "moody", "nostalgic"},
        {"romantic"},
    ]
    SAME_FAMILY_CREDIT = 0.5

    # feature name -> (UserProfile attribute, Song attribute)
    NUMERIC_FEATURES = {
        "energy": ("target_energy", "energy"),
        "valence": ("target_valence", "valence"),
        "danceability": ("target_danceability", "danceability"),
        "tempo": ("target_tempo_bpm", "tempo_bpm"),
        "acousticness": ("target_acousticness", "acousticness"),
    }

    def __init__(self, songs: List[Song]):
        """Stores the song catalog that recommendations are drawn from."""
        self.songs = songs

    @staticmethod
    def gaussian_closeness(value: float, target: float, sigma: float) -> float:
        """1.0 at an exact match, falling off smoothly as the gap grows."""
        return math.exp(-((value - target) ** 2) / (2 * sigma ** 2))

    @staticmethod
    def genre_closeness(song_genre: str, target: str) -> float:
        """Word overlap (Jaccard), so 'indie pop' vs 'pop' earns 0.5."""
        a = set(song_genre.lower().split())
        b = set(target.lower().split())
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    @classmethod
    def mood_closeness(cls, song_mood: str, target: str) -> float:
        """1.0 for the same mood, partial credit for the same mood family, else 0."""
        song_mood, target = song_mood.strip().lower(), target.strip().lower()
        if song_mood == target:
            return 1.0
        for family in cls.MOOD_FAMILIES:
            if song_mood in family and target in family:
                return cls.SAME_FAMILY_CREDIT
        return 0.0

    def closeness(self, user: UserProfile, song: Song) -> Dict[str, float]:
        """
        Per-feature closeness (0 to 1) for every preference the user set.
        Preferences that are None are left out entirely.
        """
        result: Dict[str, float] = {}
        if user.favorite_genre is not None:
            result["genre"] = self.genre_closeness(song.genre, user.favorite_genre)
        if user.favorite_mood is not None:
            result["mood"] = self.mood_closeness(song.mood, user.favorite_mood)
        for name, (user_attr, song_attr) in self.NUMERIC_FEATURES.items():
            target = getattr(user, user_attr)
            if target is not None:
                result[name] = self.gaussian_closeness(
                    getattr(song, song_attr), target, self.SIGMAS[name]
                )
        return result

    def weighted_score(self, closeness: Dict[str, float]) -> float:
        """
        Weighted average of the closeness values. Skipped preferences are left
        out of both the numerator and the denominator, so the score always
        stays between 0 and 1. No preferences at all scores 0.
        """
        total_weight = sum(self.WEIGHTS[name] for name in closeness)
        if total_weight == 0:
            return 0.0
        return sum(self.WEIGHTS[name] * c for name, c in closeness.items()) / total_weight

    def reasons(self, user: UserProfile, song: Song, closeness: Dict[str, float]) -> List[str]:
        """Human-readable reason for each scored feature, strongest match first."""
        if not closeness:
            return ["no preferences given"]

        phrases: Dict[str, str] = {}
        for name, c in closeness.items():
            if name == "genre":
                if c == 1.0:
                    phrases[name] = f"same genre ({song.genre})"
                elif c > 0:
                    phrases[name] = f"related genre ({song.genre} vs {user.favorite_genre})"
                else:
                    phrases[name] = f"different genre ({song.genre})"
            elif name == "mood":
                if c == 1.0:
                    phrases[name] = f"same mood ({song.mood})"
                elif c > 0:
                    phrases[name] = f"similar mood ({song.mood} ~ {user.favorite_mood})"
                else:
                    phrases[name] = f"different mood ({song.mood})"
            else:
                user_attr, song_attr = self.NUMERIC_FEATURES[name]
                gap = abs(getattr(song, song_attr) - getattr(user, user_attr))
                gap_text = f"{gap:.0f} BPM" if name == "tempo" else f"{gap:.2f}"
                if c >= 0.6:  # within about one sigma
                    phrases[name] = f"{name} within {gap_text} of target"
                else:
                    phrases[name] = f"{name} is {gap_text} off"

        return [phrases[name] for name in sorted(closeness, key=lambda n: -closeness[n])]

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """
        Scores a single song against the user's preferences.

        Returns (score, reasons), with reasons ordered strongest match first.
        """
        c = self.closeness(user, song)
        return self.weighted_score(c), self.reasons(user, song, c)

    def recommend_with_details(
        self, user: UserProfile, k: int = 5, min_score: float = 0.0
    ) -> List[Recommendation]:
        """
        Top k songs with their score and reasons, highest score first.

        Songs scoring below min_score are dropped, so fewer than k (or zero)
        results means nothing else in the catalog is a good enough match.
        Each song is scored once; reason text is only built for the songs
        that are returned. sorted() is stable, so ties keep catalog order.
        """
        scored = []
        for song in self.songs:
            c = self.closeness(user, song)
            s = self.weighted_score(c)
            if s >= min_score:
                scored.append((s, song, c))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            Recommendation(song=song, score=s, reasons=self.reasons(user, song, c))
            for s, song, c in scored[:k]
        ]

    def recommend(self, user: UserProfile, k: int = 5, min_score: float = 0.0) -> List[Song]:
        """Top k songs, highest score first. See recommend_with_details."""
        return [r.song for r in self.recommend_with_details(user, k, min_score)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Why the song scored as it did, strongest match first."""
        _, reasons = self.score(user, song)
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Song]:
    """
    Loads songs from a CSV file.
    Required by src/main.py

    Each row becomes a Song, with numeric columns converted so they can be
    compared against the user's targets.
    """
    songs: List[Song] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append(Song(
                id=int(row["id"]),
                title=row["title"].strip(),
                artist=row["artist"].strip(),
                genre=row["genre"].strip().lower(),
                mood=row["mood"].strip().lower(),
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
            ))
    return songs
