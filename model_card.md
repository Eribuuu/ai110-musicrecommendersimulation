# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**WaveSense 1.0** 

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration 

Currently this recommendation system is solely based on the contents of the songs ingested and recommends songs that fit closely to what parameters are defined by the user, these parameters are desired song metrics. The assumptions this recommender system takes about the user is that the user knows exactly what kind of songs they are looking for and what metrics that they are wanting in the songs (most users do not know what metrics are in songs and also would like to explore songs similar to their tastes, not exactly). This currently is not for real users based on how the system recommends songs and takes input to choose the songs to recommend, this is purely classroom exploration. To be used by actual users I would need to add a better way to set the intial values of the user profile that isn't direct numbers and values and maybe based on a song that they like already and extract values from that.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Each song has a genre, a mood, and five numbers: energy, valence (how happy or dark it sounds), danceability, tempo, and acousticness. The user says what they want for each of these, or leaves one blank to ignore it.

For every song, the system checks how close it is to what the user wants:
- **Numbers:** a perfect match gets full credit, and the credit drops off smoothly the further away the song is. Being a little off barely matters; being way off matters a lot.
- **Genre:** full credit for the same genre, half credit for a partial match like "indie pop" vs "pop".
- **Mood:** full credit for the same mood, half credit for a related mood (like "relaxed" when you asked for "chill").

Each check is then weighted by how much it matters. Mood, energy and valence count the most, genre counts half as much, and danceability, tempo and acousticness count the least. The weighted average becomes the song's score from 0 to 1. The songs are sorted by score, and the top 5 are shown with a short explanation of why each one scored the way it did.

Compared to the starter, I:
- added valence, tempo and smooth danceability/acousticness scoring (the starter only had a yes/no "likes acoustic" setting and a small danceability bonus),
- replaced the exact genre/mood matches with partial credit for related ones,
- moved mood above genre in importance (the starter weighted genre highest),
- turned the score into a 0–1 average so a preference can be left blank,
- made the explanations list every feature, closest match first, with how far off each one is.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

- The catalog has **20 songs** in `data/songs.csv`. The starter came with 10, and I added 10 more to cover more styles.
- There are **17 genres** (pop, lofi, rock, jazz, edm, metal, hip hop, classical, country, reggaeton, and more) and **16 moods** (happy, chill, intense, sad, angry, romantic, and more).
- Coverage is uneven: lofi has 3 songs, pop has 2, and every other genre has just 1.
- Missing: lyrics, language, artist popularity, release year, and many non-Western genres. Some combinations, like a high-energy sad song, don't exist in the data at all.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

- **Users with clear, common tastes get good results.** Chill Lofi got all three lofi songs on top (0.87 to 0.99), followed by other calm, acoustic songs like ambient and jazz.
- **Related moods help.** "Focused" and "relaxed" songs still showed up for a "chill" listener instead of being thrown out.
- **Opposite profiles get opposite results.** High-Energy Pop and Chill Lofi share no songs, which matches what you'd expect.
- **The explanations are easy to check.** Every recommendation says which features matched and which were off, so it's clear why a song ranked where it did.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The dataset is one of the biggest limitations at the current moment. Its very small with only 20 songs in the set and its also synthetic and not accutare or representative of real life.

**Data**
- 15 of 17 genres have only one song, so niche listeners get one good match and then filler (Deep Intense Rock drops from 0.96 to 0.56 after #1).
- Some tastes can't be met at all: no song is both high-energy and sad.
- Genres lean Western; a K-pop or Afrobeats fan gets zero genre credit on every song.

**Scoring**
- Mood, energy and valence carry about 73% of the weight, so one exact mood match can beat a song that fits every numeric target.
- Genres only match on shared words, so "rock" vs "metal" scores 0 and a pop song beat a metal song for a rock fan.
- Mood families are hand-picked by me, and "romantic" never gets partial credit.

**Output**
- It always returns k songs, even weak matches (0.29 for the rock fan), with no "no good match" signal.
- Ties keep CSV order, so songs earlier in the file win ties.
- No diversity or exploration: the same artist can repeat, and users never get pushed outside their stated taste.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

**Profiles tested**
- **High-Energy Pop:** pop, intense, energy 0.92, danceability 0.88, 130 BPM, low acousticness.
- **Chill Lofi:** lofi, chill, energy 0.38, 76 BPM, high acousticness.
- **Deep Intense Rock:** rock, intense, energy 0.92, darker valence (0.40), 150 BPM.
- I also ran edge-case profiles (conflicting preferences, unknown genres, out-of-range values, messy text, no preferences) and "tug of war" profiles that set one weight against another (results are in the README).

For each profile I checked whether the top songs matched the genre and mood I asked for, whether the songs after that still felt close, and whether the "Because" lines explained the score.

**Comparing the profiles**
- **High-Energy Pop vs Chill Lofi:** these lists don't share a single song. Pop picks loud, danceable, electronic tracks (Gym Hero, Laser Cathedral), and lofi shifts to quiet, slow, acoustic ones (Library Rain, Spacewalk Thoughts). That makes sense because the two profiles sit at opposite ends of energy, tempo and acousticness.
- **High-Energy Pop vs Deep Intense Rock:** these overlap the most. Gym Hero and Storm Runner are in both top 3s because both profiles want "intense" mood and 0.92 energy. The difference is that pop ranks Gym Hero first and rock ranks Storm Runner first, and the rest of the pop list stays bright (Sunrise City, Fuego Lento) while rock pulls in darker songs (Iron Furnace, Night Drive Loop). That fits: genre and valence are the only real differences between the two profiles.
- **Chill Lofi vs Deep Intense Rock:** these are complete opposites with no overlap. Lofi stays at 0.66 or higher for all five songs, but rock falls from 0.96 to 0.29. Both profiles have specific targets, so the gap comes from the dataset: there are three lofi songs plus several calm neighbors (ambient, jazz), while rock has one song and few intense neighbors.

**What surprised me**
- Gym Hero scored a perfect 1.00 for High-Energy Pop. My targets ended up almost identical to that one song, so the profile was really testing whether the system could find Gym Hero.
- For the rock fan, Gym Hero (pop) beat Iron Furnace (metal) even though metal sounds closer to rock. An exact "intense" mood match outweighed a similar "angry" mood, and "rock" vs "metal" gets no genre credit.
- Testing messy input (" Happy " with spaces) found a real bug: mood matching didn't ignore extra spaces. I fixed it.
- In the weight tests, a single exact mood match beat a song that matched energy almost perfectly, which showed how much mood controls the ranking.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

- **Easier user input:** build the profile from a song the user already likes instead of asking for numbers.
- **Bigger, real dataset:** more songs per genre so niche listeners get more than one good match.
- **Smarter genre matching:** treat related genres (rock and metal, hip hop and r&b) as close instead of scoring them 0.
- **Diversity:** limit songs per artist and mix in a few exploratory picks outside the user's usual taste.
- **"No good match" signal:** stop recommending songs below a minimum score instead of always returning 5.
- **Multiple tastes:** let a user have more than one profile, like "workout" and "studying".

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that a recommender is really just a set of choices about what matters: which features to compare and how much each one is weighted. Small choices have big effects. Giving mood a high weight meant a single mood label could outrank a song that fit everything else, and a small dataset meant some listeners were served much better than others for reasons that had nothing to do with their taste. It surprised me how much testing odd profiles revealed, including a real bug with extra spaces in the input. It made me realize that apps like Spotify have to balance giving people what they asked for with helping them find new music, and that the data they're built on shapes who they work well for.
