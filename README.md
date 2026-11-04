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



