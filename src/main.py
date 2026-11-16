"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

The recommendation logic lives in recommender.py:
- load_songs
- Recommender (score, recommend, explain_recommendation)
"""

from dataclasses import asdict

from recommender import UserProfile, Recommender, load_songs


# Taste profiles: the target values each song is compared against.
# Set a target to None to leave that feature out of scoring.
#   energy:       0.0 (calm) – 1.0 (intense)
#   valence:      0.0 (dark/sad) – 1.0 (bright/happy)
#   danceability: 0.0 – 1.0
#   tempo_bpm:    beats per minute
#   acousticness: 0.0 (electronic) – 1.0 (acoustic)
PROFILES = {
    "High-Energy Pop": UserProfile(
        favorite_genre="pop",
        target_energy=0.92,
        target_valence=0.75,
        target_danceability=0.88,
        target_tempo_bpm=130,
        target_acousticness=0.05,
    ),
    "Chill Lofi": UserProfile(
        favorite_genre="lofi",
        target_energy=0.38,
        target_valence=0.58,
        target_danceability=0.60,
        target_tempo_bpm=76,
        target_acousticness=0.80,
    ),
    "Deep Intense Rock": UserProfile(
        favorite_genre="rock",
        target_energy=0.92,
        target_valence=0.40,
        target_danceability=0.60,
        target_tempo_bpm=150,
        target_acousticness=0.08,
    ),
}


# Songs scoring below this are treated as "not a good match" and are not shown.
MIN_SCORE = 0.5


def print_recommendations(recommender: Recommender, name: str, user: UserProfile, k: int = 5) -> None:
    print("=" * 60)
    print(f"Profile: {name}")
    print("=" * 60)
    for field, value in asdict(user).items():
        print(f"  {field}: {value}")

    results = recommender.recommend_with_details(user, k=k, min_score=MIN_SCORE)

    print("\nTop recommendations:\n")
    if not results:
        print(f"No songs scored at least {MIN_SCORE:.2f}; nothing in the catalog is a good match.\n")
        return
    for rec in results:
        print(f"{rec.song.title} - Score: {rec.score:.2f}")
        print(f"Because: {', '.join(rec.reasons)}")
        print()
    if len(results) < k:
        print(f"(Only {len(results)} of {k} songs scored at least {MIN_SCORE:.2f}.)\n")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded Songs: {len(songs)}\n")

    recommender = Recommender(songs)

    for name, user in PROFILES.items():
        print_recommendations(recommender, name, user)


if __name__ == "__main__":
    main()
