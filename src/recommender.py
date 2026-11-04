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
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    target_danceability: float
    target_tempo_bpm: float
    target_acousticness: float

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py

    Each row becomes a dict whose keys match the Song fields, with numeric
    columns converted so they can be compared against the user's targets.
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"].strip(),
                "artist": row["artist"].strip(),
                "genre": row["genre"].strip().lower(),
                "mood": row["mood"].strip().lower(),
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

# --- Scoring constants -------------------------------------------------------
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

# feature name -> (user_prefs key, song key)
NUMERIC_FEATURES = {
    "energy": ("target_energy", "energy"),
    "valence": ("target_valence", "valence"),
    "danceability": ("target_danceability", "danceability"),
    "tempo": ("target_tempo_bpm", "tempo_bpm"),
    "acousticness": ("target_acousticness", "acousticness"),
}


def gaussian_closeness(value: float, target: float, sigma: float) -> float:
    """1.0 at an exact match, falling off smoothly as the gap grows."""
    return math.exp(-((value - target) ** 2) / (2 * sigma ** 2))


def genre_closeness(song_genre: str, target: str) -> float:
    """Word overlap (Jaccard), so 'indie pop' vs 'pop' earns 0.5."""
    a = set(song_genre.lower().split())
    b = set(target.lower().split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def mood_closeness(song_mood: str, target: str) -> float:
    """1.0 for the same mood, partial credit for the same mood family, else 0."""
    song_mood, target = song_mood.lower(), target.lower()
    if song_mood == target:
        return 1.0
    for family in MOOD_FAMILIES:
        if song_mood in family and target in family:
            return SAME_FAMILY_CREDIT
    return 0.0


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs uses the UserProfile field names. Any preference that is
    missing or None is skipped in both the numerator and the denominator of
    the weighted average, so the score always stays between 0 and 1.

    Returns (score, reasons), with reasons ordered strongest match first.
    """
    closeness: Dict[str, float] = {}
    phrases: Dict[str, str] = {}

    genre = user_prefs.get("favorite_genre")
    if genre is not None:
        c = genre_closeness(song["genre"], genre)
        closeness["genre"] = c
        if c == 1.0:
            phrases["genre"] = f"same genre ({song['genre']})"
        elif c > 0:
            phrases["genre"] = f"related genre ({song['genre']} vs {genre})"
        else:
            phrases["genre"] = f"different genre ({song['genre']})"

    mood = user_prefs.get("favorite_mood")
    if mood is not None:
        c = mood_closeness(song["mood"], mood)
        closeness["mood"] = c
        if c == 1.0:
            phrases["mood"] = f"same mood ({song['mood']})"
        elif c > 0:
            phrases["mood"] = f"similar mood ({song['mood']} ~ {mood})"
        else:
            phrases["mood"] = f"different mood ({song['mood']})"

    for name, (pref_key, song_key) in NUMERIC_FEATURES.items():
        target = user_prefs.get(pref_key)
        if target is None:
            continue
        c = gaussian_closeness(song[song_key], target, SIGMAS[name])
        closeness[name] = c
        gap = abs(song[song_key] - target)
        gap_text = f"{gap:.0f} BPM" if name == "tempo" else f"{gap:.2f}"
        if c >= 0.6:  # within about one sigma
            phrases[name] = f"{name} within {gap_text} of target"
        else:
            phrases[name] = f"{name} is {gap_text} off"

    total_weight = sum(WEIGHTS[name] for name in closeness)
    if total_weight == 0:
        return 0.0, ["no preferences given"]
    score = sum(WEIGHTS[name] * c for name, c in closeness.items()) / total_weight

    reasons = [phrases[name] for name in sorted(closeness, key=lambda n: -closeness[n])]
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Score every song: (song, score, reasons)
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Highest score first, keep the top k. sorted() is stable, so ties keep CSV order.
    top_k = sorted(scored, key=lambda rec: rec[1], reverse=True)[:k]

    return [(song, score, ", ".join(reasons)) for song, score, reasons in top_k]
