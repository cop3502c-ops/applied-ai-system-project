"""
Reliability and Testing System for the Music Recommender Simulation.

Tests:
- load_songs returns correct number of songs
- load_songs returns correct data types
- score_song gives higher score for genre match
- score_song gives higher score for mood match
- score_song rewards energy proximity correctly
- recommend_songs returns exactly k results
- recommend_songs returns results sorted highest to lowest
- diversity penalty is applied for repeated artist
- diversity penalty is applied for repeated genre
- scoring modes produce different results
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from recommender import load_songs, score_song, recommend_songs

SONGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'songs.csv')

passed = 0
failed = 0

def run_test(name, condition):
    global passed, failed
    if condition:
        print(f"  PASS: {name}")
        passed += 1
    else:
        print(f"  FAIL: {name}")
        failed += 1

print("\n" + "=" * 55)
print("  MUSIC RECOMMENDER - RELIABILITY TEST SUITE")
print("=" * 55)

# ── Load Songs Tests ──────────────────────────────────────
print("\n[1] load_songs")
songs = load_songs(SONGS_PATH)

run_test("Returns a non-empty list", len(songs) > 0)
run_test("Returns 20 songs", len(songs) == 20)
run_test("Each song has a title", all("title" in s for s in songs))
run_test("Energy is a float", all(isinstance(s["energy"], float) for s in songs))
run_test("Tempo is a float", all(isinstance(s["tempo_bpm"], float) for s in songs))
run_test("ID is an int", all(isinstance(s["id"], int) for s in songs))

# ── Score Song Tests ──────────────────────────────────────
print("\n[2] score_song")

user_pop_happy = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "target_valence": 0.80,
    "target_danceability": 0.80,
}

pop_happy_song = {"genre": "pop", "mood": "happy", "energy": 0.82, "valence": 0.84, "danceability": 0.79}
rock_intense_song = {"genre": "rock", "mood": "intense", "energy": 0.91, "valence": 0.48, "danceability": 0.66}
pop_nomatch_song = {"genre": "pop", "mood": "sad", "energy": 0.50, "valence": 0.40, "danceability": 0.50}

score_match, _ = score_song(user_pop_happy, pop_happy_song)
score_nomatch, _ = score_song(user_pop_happy, rock_intense_song)
score_genre_only, _ = score_song(user_pop_happy, pop_nomatch_song)

run_test("Genre+mood match scores higher than no match", score_match > score_nomatch)
run_test("Genre match alone scores higher than no genre match", score_genre_only > score_nomatch)
run_test("Score is a float", isinstance(score_match, float))
run_test("Score is non-negative", score_match >= 0)
run_test("Reasons string is non-empty", len(_) > 0)

# Energy proximity test
close_energy = {"genre": "jazz", "mood": "chill", "energy": 0.81, "valence": 0.50, "danceability": 0.50}
far_energy   = {"genre": "jazz", "mood": "chill", "energy": 0.20, "valence": 0.50, "danceability": 0.50}
score_close, _ = score_song(user_pop_happy, close_energy)
score_far, _   = score_song(user_pop_happy, far_energy)
run_test("Closer energy scores higher than farther energy", score_close > score_far)

# ── Scoring Modes Tests ───────────────────────────────────
print("\n[3] scoring modes")

score_balanced,     _ = score_song(user_pop_happy, pop_happy_song, mode="balanced")
score_genre_first,  _ = score_song(user_pop_happy, pop_happy_song, mode="genre_first")
score_mood_first,   _ = score_song(user_pop_happy, pop_happy_song, mode="mood_first")
score_energy_focus, _ = score_song(user_pop_happy, pop_happy_song, mode="energy_focused")

run_test("genre_first scores higher than balanced for genre match", score_genre_first > score_balanced)
run_test("mood_first scores higher than balanced for mood match", score_mood_first > score_balanced)
run_test("energy_focused produces a different score than balanced", score_energy_focus != score_balanced)

# ── Recommend Songs Tests ─────────────────────────────────
print("\n[4] recommend_songs")

results = recommend_songs(user_pop_happy, songs, k=5)
run_test("Returns exactly 5 results", len(results) == 5)
run_test("Each result is a tuple of 3", all(len(r) == 3 for r in results))
scores = [r[1] for r in results]
run_test("Results are sorted highest to lowest", scores == sorted(scores, reverse=True))
run_test("Top result has a positive score", scores[0] > 0)

results_k3 = recommend_songs(user_pop_happy, songs, k=3)
run_test("Returns exactly k=3 results", len(results_k3) == 3)

# ── Diversity Penalty Tests ───────────────────────────────
print("\n[5] diversity penalty")

lofi_user = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,
    "target_valence": 0.58,
    "target_danceability": 0.60,
}
lofi_results = recommend_songs(lofi_user, songs, k=5)
genres_in_results = [r[0]["genre"] for r in lofi_results]
lofi_count = genres_in_results.count("lofi")
run_test("Diversity penalty limits lofi genre to at most 2 in top 5", lofi_count <= 2)

artists_in_results = [r[0]["artist"] for r in lofi_results]
run_test("No artist appears more than once in top 5", len(artists_in_results) == len(set(artists_in_results)))

penalty_triggered = any("repeat" in r[2] for r in lofi_results)
run_test("Penalty reason appears in explanation when triggered", penalty_triggered)

# ── Summary ───────────────────────────────────────────────
print("\n" + "=" * 55)
total = passed + failed
print(f"  Results: {passed}/{total} tests passed")
if failed == 0:
    print("  All tests passed.")
else:
    print(f"  {failed} test(s) failed. Review output above.")
print("=" * 55 + "\n")