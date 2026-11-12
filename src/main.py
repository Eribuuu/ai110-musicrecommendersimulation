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
        favorite_mood="intense",
        target_energy=0.92,
        target_valence=0.75,
        target_danceability=0.88,
        target_tempo_bpm=130,
        target_acousticness=0.05,
    ),
    "Chill Lofi": UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.38,
        target_valence=0.58,
        target_danceability=0.60,
        target_tempo_bpm=76,
        target_acousticness=0.80,
    ),
    "Deep Intense Rock": UserProfile(
        favorite_genre="rock",
        favorite_mood="intense",
        target_energy=0.92,
        target_valence=0.40,
        target_danceability=0.60,
        target_tempo_bpm=150,
        target_acousticness=0.08,
    ),
}


def print_recommendations(recommender: Recommender, name: str, user: UserProfile, k: int = 5) -> None:
    print("=" * 60)
    print(f"Profile: {name}")
    print("=" * 60)
    for field, value in asdict(user).items():
        print(f"  {field}: {value}")

    print("\nTop recommendations:\n")
    for song in recommender.recommend(user, k=k):
        score, _ = recommender.score(user, song)
        print(f"{song.title} - Score: {score:.2f}")
        print(f"Because: {recommender.explain_recommendation(user, song)}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded Songs: {len(songs)}\n")

    recommender = Recommender(songs)

    for name, user in PROFILES.items():
        print_recommendations(recommender, name, user)


if __name__ == "__main__":
    main()
