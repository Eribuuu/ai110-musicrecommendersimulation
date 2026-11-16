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

    # Genre, energy and valence are the strongest signals. Tempo and acousticness
    # mostly duplicate energy in this dataset, so they stay low.
    WEIGHTS = {
        "genre": 2.0,
        "energy": 2.0,
        "valence": 2.0,
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

    # Genre closeness compares each genre's centroid: the average of its songs'
    # standardized audio features. Two genres one sigma apart score ~0.61, where
    # sigma = GENRE_SIGMA_SCALE * the median distance between genre centroids,
    # so the tolerance adapts to how spread out the catalog's genres are.
    GENRE_FEATURES = ["energy", "valence", "danceability", "acousticness", "tempo_bpm"]
    GENRE_SIGMA_SCALE = 0.5

    # feature name -> (UserProfile attribute, Song attribute)
    NUMERIC_FEATURES = {
        "energy": ("target_energy", "energy"),
        "valence": ("target_valence", "valence"),
        "danceability": ("target_danceability", "danceability"),
        "tempo": ("target_tempo_bpm", "tempo_bpm"),
        "acousticness": ("target_acousticness", "acousticness"),
    }

    def __init__(self, songs: List[Song]):
        """Stores the song catalog and precomputes how close each pair of genres is."""
        self.songs = songs
        self.genre_similarity: Dict[Tuple[str, str], float] = self._build_genre_similarity()

    def _build_genre_similarity(self) -> Dict[Tuple[str, str], float]:
        """
        Similarity (0 to 1) for every pair of genres in the catalog.

        1. Standardize each feature across all songs (z-score), so tempo's BPM
           scale doesn't outweigh the 0-1 features.
        2. Average each genre's standardized songs into a centroid.
        3. Turn each centroid distance into a Gaussian closeness.
        """
        if not self.songs:
            return {}

        means, stds = {}, {}
        for f in self.GENRE_FEATURES:
            values = [getattr(s, f) for s in self.songs]
            means[f] = sum(values) / len(values)
            std = math.sqrt(sum((v - means[f]) ** 2 for v in values) / len(values))
            stds[f] = std or 1.0  # every song identical on this feature

        by_genre: Dict[str, List[List[float]]] = {}
        for s in self.songs:
            vec = [(getattr(s, f) - means[f]) / stds[f] for f in self.GENRE_FEATURES]
            by_genre.setdefault(self._normalize_genre(s.genre), []).append(vec)
        centroids = {
            g: [sum(col) / len(vecs) for col in zip(*vecs)] for g, vecs in by_genre.items()
        }

        genres = sorted(centroids)
        distances = {
            (a, b): math.dist(centroids[a], centroids[b])
            for i, a in enumerate(genres)
            for b in genres[i + 1:]
        }

        similarity = {(g, g): 1.0 for g in genres}
        if not distances:  # only one genre in the catalog
            return similarity

        ordered = sorted(distances.values())
        mid = len(ordered) // 2
        median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
        sigma = self.GENRE_SIGMA_SCALE * median or 1.0  # all centroids identical

        for (a, b), d in distances.items():
            similarity[(a, b)] = similarity[(b, a)] = self.gaussian_closeness(d, 0.0, sigma)
        return similarity

    @staticmethod
    def _normalize_genre(genre: str) -> str:
        """Lowercase and collapse whitespace, so ' Hip  Hop' matches 'hip hop'."""
        return " ".join(genre.lower().split())

    @staticmethod
    def gaussian_closeness(value: float, target: float, sigma: float) -> float:
        """1.0 at an exact match, falling off smoothly as the gap grows."""
        return math.exp(-((value - target) ** 2) / (2 * sigma ** 2))

    def genre_closeness(self, song_genre: str, target: str) -> float:
        """
        How close two genres are, from 0 to 1.

        Genres in the catalog are compared by centroid. A genre the catalog has
        never seen (e.g. a user asking for 'k-pop') falls back to word overlap
        (Jaccard), so 'indie pop' vs 'pop' still earns 0.5.
        """
        a, b = self._normalize_genre(song_genre), self._normalize_genre(target)
        if a == b:
            return 1.0 if a else 0.0
        if (a, b) in self.genre_similarity:
            return self.genre_similarity[(a, b)]
        words_a, words_b = set(a.split()), set(b.split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / len(words_a | words_b)

    def similar_genres(self, genre: str, n: int = 5) -> List[Tuple[str, float]]:
        """The n catalog genres closest to `genre` (excluding itself), closest first."""
        g = self._normalize_genre(genre)
        matches = [(b, s) for (a, b), s in self.genre_similarity.items() if a == g and b != g]
        return sorted(matches, key=lambda m: -m[1])[:n]

    def closeness(self, user: UserProfile, song: Song) -> Dict[str, float]:
        """
        Per-feature closeness (0 to 1) for every preference the user set.
        Preferences that are None are left out entirely.
        """
        result: Dict[str, float] = {}
        if user.favorite_genre is not None:
            result["genre"] = self.genre_closeness(song.genre, user.favorite_genre)
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
                elif c >= 0.6:  # centroids within about one sigma
                    phrases[name] = f"similar genre ({song.genre} ~ {user.favorite_genre})"
                else:
                    phrases[name] = f"different genre ({song.genre})"
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
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
            ))
    return songs
