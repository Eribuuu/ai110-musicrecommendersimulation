from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
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
        target_energy=0.8,
        target_valence=0.9,
        target_danceability=0.8,
        target_tempo_bpm=120,
        target_acousticness=0.2,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, high energy song should score higher
    assert results[0].genre == "pop"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
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
    empty = UserProfile(None, None, None, None, None, None)
    score, reasons = rec.score(empty, rec.songs[0])

    assert score == 0.0
    assert reasons == ["no preferences given"]
    assert rec.recommend_with_details(empty, k=2, min_score=0.1) == []


def make_song(id, genre, energy, valence, danceability, acousticness, tempo_bpm) -> Song:
    return Song(
        id=id, title=f"Song {id}", artist="Test Artist", genre=genre,
        energy=energy, tempo_bpm=tempo_bpm, valence=valence,
        danceability=danceability, acousticness=acousticness,
    )


def make_genre_recommender() -> Recommender:
    return Recommender([
        make_song(1, "rock", 0.90, 0.45, 0.60, 0.10, 150),
        make_song(2, "rock", 0.85, 0.50, 0.55, 0.15, 140),
        make_song(3, "metal", 0.95, 0.30, 0.50, 0.05, 165),
        make_song(4, "pop", 0.80, 0.85, 0.85, 0.15, 120),
        make_song(5, "lofi", 0.35, 0.60, 0.60, 0.85, 75),
        make_song(6, "lofi", 0.40, 0.55, 0.62, 0.80, 80),
    ])


def test_same_genre_is_full_credit():
    rec = make_genre_recommender()
    assert rec.genre_closeness("rock", "rock") == 1.0
    assert rec.genre_closeness(" Rock ", "rock") == 1.0


def test_metal_is_closer_to_rock_than_lofi():
    rec = make_genre_recommender()
    assert rec.genre_closeness("metal", "rock") > rec.genre_closeness("lofi", "rock")
    assert rec.similar_genres("rock", n=1)[0][0] == "metal"


def test_genre_closeness_is_symmetric_and_bounded():
    rec = make_genre_recommender()
    genres = ["rock", "metal", "pop", "lofi"]
    for a in genres:
        for b in genres:
            c = rec.genre_closeness(a, b)
            assert 0.0 <= c <= 1.0
            assert c == rec.genre_closeness(b, a)


def test_unknown_genre_falls_back_to_word_overlap():
    rec = make_genre_recommender()
    assert rec.genre_closeness("indie pop", "pop") == 0.5
    assert rec.genre_closeness("k-pop", "rock") == 0.0


def test_single_genre_catalog_does_not_crash():
    one = Recommender([make_song(1, "rock", 0.9, 0.4, 0.6, 0.1, 150)])
    assert one.genre_closeness("rock", "rock") == 1.0
    assert one.similar_genres("rock") == []
    assert Recommender([]).genre_closeness("rock", "pop") == 0.0
