import json
import tempfile
import unittest
from pathlib import Path

from app import Exercise, ExerciseStore, count_words


class WordCountTests(unittest.TestCase):
    def test_empty_text(self):
        self.assertEqual(count_words(""), 0)

    def test_sentences_and_whitespace(self):
        self.assertEqual(count_words("One two\nthree.  Four!"), 4)

    def test_contractions_and_hyphenated_words(self):
        self.assertEqual(count_words("Don't rewrite this well-written sentence."), 5)

    def test_unicode_words(self):
        self.assertEqual(count_words("سلام دنیا — café naïve"), 4)


class StoreTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data" / "exercises.json"
            store = ExerciseStore(path)
            exercise = Exercise.create("My exercise")
            exercise.content = "A short writing exercise."
            exercise.target_words = 400
            exercise.elapsed_seconds = 15

            store.save([exercise])
            loaded = store.load()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].title, "My exercise")
            self.assertEqual(loaded[0].content, "A short writing exercise.")
            self.assertEqual(loaded[0].target_words, 400)
            self.assertEqual(loaded[0].elapsed_seconds, 15)
            self.assertEqual(json.loads(path.read_text())["version"], 1)

    def test_unreadable_file_is_backed_up_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exercises.json"
            path.write_text('{"exercises": [ broken', encoding="utf-8")
            store = ExerciseStore(path)

            self.assertEqual(store.load(), [])
            self.assertIsNotNone(store.backup_path)
            self.assertFalse(path.exists())
            self.assertEqual(store.backup_path.read_text(encoding="utf-8"), '{"exercises": [ broken')

    def test_invalid_exercise_is_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exercises.json"
            path.write_text(json.dumps({"version": 1, "exercises": [
                {"id": "a", "title": "Good"},
                {"id": "b", "title": "Bad", "target_words": "lots"},
            ]}), encoding="utf-8")

            loaded = ExerciseStore(path).load()

            self.assertEqual([exercise.title for exercise in loaded], ["Good"])


if __name__ == "__main__":
    unittest.main()
