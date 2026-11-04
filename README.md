# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.

From my understanding of how real world recommendation systems work, these systems utilize two large compenents to be able to recommend and predict what someone will like (in the instance, music).
One component is collaborative filtering, this is where whatever platform builds a large matrix based on users and their songs (whatever is being recommended by the system). The matrix takes into account plays, skips, playlist adds and other metrics and compares them to how other people interact with the song as well. Based on how others interact with the song and how you interact with the song, the system can match other songs to you that the other users have interacted positively with (played the song fully, added to a playlist, etc.). The other component is content based filtering/analysis which is what this project will focus on. This aspect of a recommendation system recommends based on the song's content itself. A song has different metrics that can be used to score a song (such as danceability or energy). A user can have preferences on what they like in certain songs (in this case this is set explicitly but in larger systems this would be something that is accumulated based on what the user listens to) and the recommender will suggest sonsg that match or is close to those preferences.

Song Object Features:
- Mood
- Energy
- Valence
- Genre
- Danceability
- Tempo
- acousticness

UserProfile Features:
- favorite genere
- favorite mood
- target energy (since its explicitly stated in this simulation)
- target valence (since its explicitly stated in this simulation)
- target danceability (since its explicitly stated in this simulation)
- target tempo bpm (since its explicitly stated in this simulation)
- target acousticness (since its explicitly stated in this simulation)

### Algorithm Recipe

**Scoring (one song vs. one user profile):**

1. For each feature the user set a target for, compute a closeness from 0 to 1. Targets left as `None` are skipped.
   - **Numeric features** (energy, valence, danceability, acousticness, tempo) use Gaussian closeness, `exp(-(gap)² / 2σ²)`. σ is 0.15 for the 0–1 features and 15 BPM for tempo, so a small gap costs little and a large gap costs a lot.
   - **Genre** is the word overlap between the two genres, so "indie pop" vs "pop" scores 0.5.
   - **Mood** scores 1.0 for an exact match, 0.5 if both moods are in the same mood family (e.g. {chill, relaxed, focused, peaceful}), and 0 otherwise.
2. Combine the closeness values in a weighted average: `score = Σ(weight × closeness) / Σ(weights used)`. The weights are:

   | Feature | Weight | Why |
   |---|---|---|
   | mood | 2.0 | strongest signal of what a listener wants |
   | energy | 2.0 | main calm-vs-intense axis |
   | valence | 2.0 | separates happy from dark songs at the same energy |
   | genre | 1.0 | |
   | danceability | 0.75 | partly tracks energy |
   | tempo | 0.25 | mostly duplicates energy |
   | acousticness | 0.25 | nearly the inverse of energy in this data |

**Ranking (the whole list):**

1. Drop songs the user has already heard.
2. Drop songs below the minimum score (0 by default).
3. Sort by score, highest first, breaking ties alphabetically by title.
4. Allow at most 2 songs per artist.
5. Return the top k, each with an explanation built from its per-feature closeness values.

```
songs.csv ─load_songs─▶ [Song × 20]
                            │  + UserProfile + ScoringConfig
                            ▼
                     score each song ──▶ [ScoredSong × 20]
                            ▼
                     rank: exclude → threshold → sort → diversity → top k
                            ▼
                     explain ──▶ [(song, score, "because …") × k]
```

### Potential Biases

- **Mood and energy outweigh genre.** Mood, energy and valence together carry about 70% of the weight, so a song in the user's favorite genre with the "wrong" mood can lose to a song from an unrelated genre. For example, a pop fan who wants happy music may see reggaeton ranked above an intense pop track.
- **The mood families are hand-written opinions.** Which moods count as "related" reflects my judgment, not data, and a mood outside any family (e.g. romantic) never gets partial credit.
- **Genres only match on shared words.** "rock" vs "metal" or "hip hop" vs "r&b" score 0, even though listeners often hear them as close.
- **The catalog is small and uneven.** Most genres have a single song, so users with niche tastes get only one strong match and the rest of their list is filler.
- **There is no exploration.** The system only recommends what is closest to the stated profile, so it can never surprise a user or help their taste grow (a filter bubble).

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



