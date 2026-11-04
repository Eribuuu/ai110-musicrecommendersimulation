"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 
    print(f"Loaded Songs: {len(songs)}")

    # Taste profile: the target values each song is compared against.
    # Keys mirror the UserProfile fields in recommender.py.
    # Set a target to None to leave that feature out of scoring.
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,        # 0.0 (calm) – 1.0 (intense)
        "target_valence": 0.80,       # 0.0 (dark/sad) – 1.0 (bright/happy)
        "target_danceability": 0.75,  # 0.0 – 1.0
        "target_tempo_bpm": 120,      # beats per minute
        "target_acousticness": 0.20,  # 0.0 (electronic) – 1.0 (acoustic)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
