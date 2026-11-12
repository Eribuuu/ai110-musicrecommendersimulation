"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

The recommendation logic lives in recommender.py:
- load_songs
- Recommender (score, recommend, explain_recommendation)
"""

from recommender import UserProfile, Recommender, load_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded Songs: {len(songs)}")

    # Taste profile: the target values each song is compared against.
    # Set a target to None to leave that feature out of scoring.
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.80,        # 0.0 (calm) – 1.0 (intense)
        target_valence=0.80,       # 0.0 (dark/sad) – 1.0 (bright/happy)
        target_danceability=0.75,  # 0.0 – 1.0
        target_tempo_bpm=120,      # beats per minute
        target_acousticness=0.20,  # 0.0 (electronic) – 1.0 (acoustic)
    )

    recommender = Recommender(songs)

    print("\nTop recommendations:\n")
    for song in recommender.recommend(user, k=5):
        score, _ = recommender.score(user, song)
        print(f"{song.title} - Score: {score:.2f}")
        print(f"Because: {recommender.explain_recommendation(user, song)}")
        print()


if __name__ == "__main__":
    main()
