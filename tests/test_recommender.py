from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_tempo_bpm=120,
        target_acousticness=0.2,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_tempo_bpm=120,
        target_acousticness=0.2,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


POP_USER = UserProfile(
    favorite_genre="pop",
    favorite_mood="happy",
    target_energy=0.8,
    target_valence=0.9,
    target_danceability=0.8,
    target_tempo_bpm=120,
    target_acousticness=0.2,
)


def test_recommend_with_details_matches_score():
    rec = make_small_recommender()
    results = rec.recommend_with_details(POP_USER, k=2)

    assert [r.song for r in results] == rec.recommend(POP_USER, k=2)
    for r in results:
        score, reasons = rec.score(POP_USER, r.song)
        assert r.score == score
        assert r.reasons == reasons
    assert results[0].score >= results[1].score


def test_min_score_drops_weak_matches():
    rec = make_small_recommender()
    results = rec.recommend_with_details(POP_USER, k=2, min_score=0.5)

    # The exact pop match passes; the lofi song is far off on every feature.
    assert len(results) == 1
    assert results[0].song.genre == "pop"


def test_min_score_can_return_nothing():
    rec = make_small_recommender()
    assert rec.recommend_with_details(POP_USER, k=2, min_score=1.01) == []


def test_no_preferences_scores_zero():
    rec = make_small_recommender()
    empty = UserProfile(None, None, None, None, None, None, None)
    score, reasons = rec.score(empty, rec.songs[0])

    assert score == 0.0
    assert reasons == ["no preferences given"]
    assert rec.recommend_with_details(empty, k=2, min_score=0.1) == []
