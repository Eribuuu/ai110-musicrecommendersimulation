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
Loaded Songs: 20

User profile:
  favorite_genre: pop
  favorite_mood: happy
  target_energy: 0.8
  target_valence: 0.8
  target_danceability: 0.75
  target_tempo_bpm: 120
  target_acousticness: 0.2

Top recommendations:

Sunrise City - Score: 0.99
Because: same genre (pop), same mood (happy), energy within 0.02 of target, tempo within 2 BPM of target, acousticness within 0.02 sof target, valence within 0.04 of target, danceability within 0.04 of target

Rooftop Lights - Score: 0.91
Because: same mood (happy), valence within 0.01 of target, tempo within 4 BPM of target, energy within 0.04 of target, danceability within 0.07 of target, acousticness within 0.15 of target, related genre (indie pop vs pop)

Fuego Lento - Score: 0.68
Because: valence within 0.01 of target, energy within 0.04 of target, acousticness within 0.05 of target, danceability is 0.17 off, similar mood (energetic ~ happy), tempo is 24 BPM off, different genre (reggaeton)

Gym Hero - Score: 0.63
Because: same genre (pop), valence within 0.03 of target, tempo within 12 BPM of target, energy within 0.13 of target, danceability within 0.13 of target, acousticness within 0.15 of target, different mood (intense)

Concrete Crown - Score: 0.58
Because: energy within 0.02 of target, acousticness within 0.08 of target, danceability within 0.11 of target, similar mood (confident ~ happy), valence is 0.18 off, tempo is 26 BPM off, different genre (hip hop)
```


**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

Here is the weigths being tested against each other, showing how each weight effects the scoring and which ones are more significant or matter compared to each other.

```
Loaded Songs: 20

============================================================
Profile: High-Energy Pop
============================================================
  favorite_genre: pop
  favorite_mood: intense
  target_energy: 0.92
  target_valence: 0.75
  target_danceability: 0.88
  target_tempo_bpm: 130
  target_acousticness: 0.05

Top recommendations:

Gym Hero - Score: 1.00
Because: same genre (pop), same mood (intense), danceability within 0.00 of target, acousticness within 0.00 of target, energy within 0.01 of target, valence within 0.02 of target, tempo within 2 BPM of target

Sunrise City - Score: 0.64
Because: same genre (pop), valence within 0.09 of target, danceability within 0.09 of target, energy within 0.10 of target, tempo within 12 BPM of target, acousticness within 0.13 of target, different mood (happy)

Storm Runner - Score: 0.60
Because: same mood (intense), energy within 0.01 of target, acousticness within 0.05 of target, danceability is 0.22 off, tempo is22 BPM off, valence is 0.27 off, different genre (rock)

Fuego Lento - Score: 0.56
Because: valence within 0.04 of target, danceability within 0.04 of target, energy within 0.08 of target, acousticness within 0.10of target, tempo is 34 BPM off, different genre (reggaeton), different mood (energetic)

Laser Cathedral - Score: 0.54
Because: tempo within 2 BPM of target, acousticness within 0.03 of target, energy within 0.05 of target, danceability within 0.06 of target, valence within 0.13 of target, different genre (edm), different mood (euphoric)

============================================================
Profile: Chill Lofi
============================================================
  favorite_genre: lofi
  favorite_mood: chill
  target_energy: 0.38
  target_valence: 0.58
  target_danceability: 0.6
  target_tempo_bpm: 76
  target_acousticness: 0.8

Top recommendations:

Library Rain - Score: 0.99
Because: same genre (lofi), same mood (chill), valence within 0.02 of target, danceability within 0.02 of target, energy within 0.03 of target, tempo within 4 BPM of target, acousticness within 0.06 of target

Midnight Coding - Score: 0.98
Because: same genre (lofi), same mood (chill), valence within 0.02 of target, danceability within 0.02 of target, tempo within 2 BPM of target, energy within 0.04 of target, acousticness within 0.09 of target

Focus Flow - Score: 0.87
Because: same genre (lofi), danceability within 0.00 of target, valence within 0.01 of target, energy within 0.02 of target, acousticness within 0.02 of target, tempo within 4 BPM of target, similar mood (focused ~ chill)

Spacewalk Thoughts - Score: 0.73
Because: same mood (chill), valence within 0.07 of target, energy within 0.10 of target, acousticness within 0.12 of target, tempois 16 BPM off, danceability is 0.19 off, different genre (ambient)

Coffee Shop Stories - Score: 0.66
Because: energy within 0.01 of target, danceability within 0.06 of target, acousticness within 0.09 of target, valence within 0.13of target, tempo within 14 BPM of target, similar mood (relaxed ~ chill), different genre (jazz)

============================================================
Profile: Deep Intense Rock
============================================================
  favorite_genre: rock
  favorite_mood: intense
  target_energy: 0.92
  target_valence: 0.4
  target_danceability: 0.6
  target_tempo_bpm: 150
  target_acousticness: 0.08

Top recommendations:

Storm Runner - Score: 0.96
Because: same genre (rock), same mood (intense), energy within 0.01 of target, tempo within 2 BPM of target, acousticness within 0.02 of target, danceability within 0.06 of target, valence within 0.08 of target

Gym Hero - Score: 0.56
Because: same mood (intense), energy within 0.01 of target, acousticness within 0.03 of target, tempo is 18 BPM off, danceability is 0.28 off, valence is 0.37 off, different genre (pop)

Iron Furnace - Score: 0.53
Because: acousticness within 0.05 of target, energy within 0.07 of target, danceability within 0.15 of target, similar mood (angry~ intense), valence is 0.19 off, tempo is 34 BPM off, different genre (metal)

Night Drive Loop - Score: 0.41
Because: valence within 0.09 of target, danceability within 0.13 of target, acousticness within 0.14 of target, energy is 0.17 off, tempo is 40 BPM off, different genre (synthwave), different mood (moody)

Concrete Crown - Score: 0.29
Because: acousticness within 0.04 of target, energy within 0.14 of target, valence is 0.22 off, danceability is 0.26 off, tempo is56 BPM off, different genre (hip hop), different mood (confident)


############################################################
# WEIGHT STRESS TESTS
############################################################

============================================================
Profile: Genre vs Mood
============================================================
  favorite_genre: lofi
  favorite_mood: intense
  target_energy: None
  target_valence: None
  target_danceability: None
  target_tempo_bpm: None
  target_acousticness: None

Top recommendations:

Storm Runner - Score: 0.67
Because: same mood (intense), different genre (rock)

Gym Hero - Score: 0.67
Because: same mood (intense), different genre (pop)

Midnight Coding - Score: 0.33
Because: same genre (lofi), different mood (chill)

Head to head:
  [genre] Midnight Coding - Score: 0.33 (rank 3 of 20)
    Because: same genre (lofi), different mood (chill)
  [mood] Storm Runner - Score: 0.67 (rank 1 of 20)
    Because: same mood (intense), different genre (rock)

============================================================
Profile: Genre vs Energy
============================================================
  favorite_genre: classical
  favorite_mood: None
  target_energy: 0.95
  target_valence: None
  target_danceability: None
  target_tempo_bpm: None
  target_acousticness: None

Top recommendations:

Gym Hero - Score: 0.66
Because: energy within 0.02 of target, different genre (pop)

Laser Cathedral - Score: 0.66
Because: energy within 0.02 of target, different genre (edm)

Storm Runner - Score: 0.64
Because: energy within 0.04 of target, different genre (rock)

Head to head:
  [genre] Nocturne in Grey - Score: 0.33 (rank 8 of 20)
    Because: same genre (classical), energy is 0.77 off
  [energy] Laser Cathedral - Score: 0.66 (rank 2 of 20)
    Because: energy within 0.02 of target, different genre (edm)

============================================================
Profile: Mood vs Energy (equal weights)
============================================================
  favorite_genre: None
  favorite_mood: peaceful
  target_energy: 0.95
  target_valence: None
  target_danceability: None
  target_tempo_bpm: None
  target_acousticness: None

Top recommendations:

Nocturne in Grey - Score: 0.50
Because: same mood (peaceful), energy is 0.77 off

Gym Hero - Score: 0.50
Because: energy within 0.02 of target, different mood (intense)

Laser Cathedral - Score: 0.50
Because: energy within 0.02 of target, different mood (euphoric)

Head to head:
  [mood] Nocturne in Grey - Score: 0.50 (rank 1 of 20)
    Because: same mood (peaceful), energy is 0.77 off
  [energy] Laser Cathedral - Score: 0.50 (rank 3 of 20)
    Because: energy within 0.02 of target, different mood (euphoric)

============================================================
Profile: Energy vs All Minor Features
============================================================
  favorite_genre: None
  favorite_mood: None
  target_energy: 0.18
  target_valence: None
  target_danceability: 0.92
  target_tempo_bpm: 96
  target_acousticness: 0.15

Top recommendations:

Nocturne in Grey - Score: 0.63
Because: energy within 0.00 of target, tempo is 30 BPM off, danceability is 0.70 off, acousticness is 0.82 off

Paper Boats - Score: 0.52
Because: tempo within 2 BPM of target, energy within 0.12 of target, danceability is 0.48 off, acousticness is 0.76 off

Spacewalk Thoughts - Score: 0.50
Because: energy within 0.10 of target, tempo is 36 BPM off, danceability is 0.51 off, acousticness is 0.77 off

Head to head:
  [energy] Nocturne in Grey - Score: 0.63 (rank 1 of 20)
    Because: energy within 0.00 of target, tempo is 30 BPM off, danceability is 0.70 off, acousticness is 0.82 off
  [minor features] Fuego Lento - Score: 0.38 (rank 4 of 20)
    Because: danceability within 0.00 of target, tempo within 0 BPM of target, acousticness within 0.00 of target, energy is 0.66 off

============================================================
Profile: Big Three vs Everything Else
============================================================
  favorite_genre: pop
  favorite_mood: sad
  target_energy: 0.46
  target_valence: 0.18
  target_danceability: 0.88
  target_tempo_bpm: 132
  target_acousticness: 0.05

Top recommendations:

Crossroads at Midnight - Score: 0.73
Because: same mood (sad), energy within 0.00 of target, valence within 0.00 of target, danceability is 0.38 off, tempo is 62 BPM off, acousticness is 0.69 off, different genre (blues)

Paper Boats - Score: 0.42
Because: valence within 0.14 of target, energy is 0.16 off, similar mood (melancholic ~ sad), tempo is 34 BPM off, danceability is0.44 off, acousticness is 0.86 off, different genre (folk)

Dusty Porch Swing - Score: 0.35
Because: energy within 0.09 of target, similar mood (nostalgic ~ sad), danceability is 0.27 off, tempo is 28 BPM off, valence is 0.56 off, acousticness is 0.63 off, different genre (country)

Head to head:
  [big three] Crossroads at Midnight - Score: 0.73 (rank 1 of 20)
    Because: same mood (sad), energy within 0.00 of target, valence within 0.00 of target, danceability is 0.38 off, tempo is 62 BPM off, acousticness is 0.69 off, different genre (blues)
  [everything else] Gym Hero - Score: 0.27 (rank 5 of 20)
    Because: same genre (pop), danceability within 0.00 of target, tempo within 0 BPM of target, acousticness within 0.00 of target, energy is 0.47 off, valence is 0.59 off, different mood (intense)
```

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



