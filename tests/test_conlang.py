#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Conlang Phonotactics & Sound-Change Applier (scripts/lib/conlang.py).
Covers phonotactic word/name generation, cluster filtering, historical sound shift rules,
lexicon extraction, CSV/Markdown exporting, family trees, and CLI entry points.
"""

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.conlang import (
    generate_words,
    generate_syllable,
    load_conlang_profile,
    load_all_conlangs,
    mutate_text,
    compile_sound_rule,
    print_family_tree,
    main
)


class TestConlangEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.lang_dir = self.world_dir / "Languages"
        self.lang_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_conlang_profile(self) -> None:
        """load_conlang_profile parses phoneme inventories, clusters, and markdown lexicon table."""
        (self.lang_dir / "Solar_Tongue.md").write_text("""---
name: "Solar Tongue"
type: language
consonants: [k, l, r, m, n, s, v, th]
vowels: [a, e, i, o, u]
syllable_structures: ["CV", "CVC"]
forbidden_clusters: ["thk", "sr"]
stress_rule: "penultimate"
sound_changes:
  - "k > ch / _[e,i]"
---
# Solar Tongue
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Aethel* | Noun | /ˈaɪ.θəl/ | Sun King | Royal honorific |
| *Vaelor* | Noun | /ˈvaɪ.lɔːr/ | Shield | Military vow |
""", encoding="utf-8")

        profile = load_conlang_profile(self.world_dir, "Solar")
        self.assertEqual(profile["name"], "Solar Tongue")
        self.assertIn("k", profile["consonants"])
        self.assertIn("CV", profile["syllable_structures"])
        self.assertIn("thk", profile["forbidden_clusters"])
        self.assertEqual(len(profile["lexicon"]), 2)
        self.assertEqual(profile["lexicon"][0]["word"], "Aethel")

    def test_load_conlang_profile_from_bible_dir_and_comma_strings(self) -> None:
        bible_dir = self.world_dir / "00-World-Bible" / "Languages"
        bible_dir.mkdir(parents=True)
        (bible_dir / "Lunar.md").write_text("""---
name: "Lunar"
consonants: "p, t, k, m, n"
vowels: "a, i, u"
syllables: "CV, V"
forbidden_clusters: "pt, km"
sound_changes: "p > b / V_V; t > d / V_V"
---
# Lunar
## Lexicon
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Luna* | Noun | /ˈluː.nə/ | Moon | Celestial |
""", encoding="utf-8")

        profile = load_conlang_profile(self.world_dir, "Lunar")
        self.assertEqual(profile["name"], "Lunar")
        self.assertEqual(len(profile["consonants"]), 5)
        self.assertEqual(len(profile["vowels"]), 3)
        self.assertEqual(len(profile["forbidden_clusters"]), 2)
        self.assertEqual(len(profile["sound_changes"]), 2)
        self.assertEqual(len(profile["lexicon"]), 1)

    def test_load_conlang_profile_not_found_raises(self) -> None:
        """load_conlang_profile raises FileNotFoundError when language note does not exist."""
        with self.assertRaises(FileNotFoundError):
            load_conlang_profile(self.world_dir, "NonexistentLang")

    def test_generate_words_phonotactics(self) -> None:
        """generate_words produces legal syllables and excludes banned phonetic clusters."""
        profile = {
            "name": "Valen",
            "consonants": ["p", "t", "k", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC"],
            "forbidden_clusters": ["sr", "kp"],
        }
        words = generate_words(profile, count=15, num_syllables=2, word_type="name", seed=42)
        self.assertEqual(len(words), 15)
        for w in words:
            self.assertTrue(w.istitle())
            self.assertNotIn("sr", w.lower())
            self.assertNotIn("kp", w.lower())

        # Test place type
        places = generate_words(profile, count=5, num_syllables=2, word_type="place", seed=100)
        self.assertEqual(len(places), 5)
        for p in places:
            self.assertTrue(p.istitle())

    def test_generate_words_deterministic_seed(self) -> None:
        """Providing an identical integer seed reproduces the exact word list."""
        profile = {
            "name": "Valen",
            "consonants": ["p", "t", "k", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC"],
            "forbidden_clusters": [],
        }
        words1 = generate_words(profile, count=10, seed=1234)
        words2 = generate_words(profile, count=10, seed=1234)
        self.assertEqual(words1, words2)

    def test_generate_syllable_unknown_char(self) -> None:
        import random
        syl = generate_syllable("C-V", ["k"], ["a"], random.Random(42))
        self.assertEqual(syl, "k-a")

    def test_sound_change_intervocalic_voicing(self) -> None:
        """p > b between vowels (V_V) mutates apata to abata while preserving word-initial p."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "b", "d", "g", "s", "m", "n", "l", "r"]
        rules = ["p > b / V_V"]
        res = mutate_text("apata", rules, vowels, consonants)
        self.assertEqual(res, "abata")

        res2 = mutate_text("pata", rules, vowels, consonants)
        self.assertEqual(res2, "pata")

        res3 = mutate_text("apapapa", rules, vowels, consonants)
        self.assertEqual(res3, "abababa")

    def test_sound_change_palatalization(self) -> None:
        """k > ch before front vowels e/i (_[e,i]) mutates keli to cheli but keeps kora."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "ch", "b", "d", "s", "m", "n", "l", "r"]
        rules = ["k > ch / _[e,i]"]
        self.assertEqual(mutate_text("keli", rules, vowels, consonants), "cheli")
        self.assertEqual(mutate_text("kora", rules, vowels, consonants), "kora")

    def test_sound_change_word_initial(self) -> None:
        """s > h word-initially (#_) mutates solas to holas."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["s > h / #_"]
        self.assertEqual(mutate_text("solas", rules, vowels, consonants), "holas")

    def test_sound_change_word_final_deletion(self) -> None:
        """e > 0 word-finally (_#) mutates mate to mat."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        rules = ["e > 0 / _#", "a > null / _#", "i > none / _#", "o > Ø / _#"]
        self.assertEqual(mutate_text("mate", rules, vowels, consonants), "mat")

    def test_sound_change_wildcard_source(self) -> None:
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["s", "h", "p", "t", "k", "l", "m", "n"]
        # V > e at end of word
        rules_v = ["V > e / _#"]
        self.assertEqual(mutate_text("pata", rules_v, vowels, consonants), "pate")
        # C > x before vowel
        rules_c = ["C > x / _V"]
        self.assertEqual(mutate_text("pata", rules_c, vowels, consonants), "xaxa")

    def test_sound_change_word_initial_with_following_vowel(self) -> None:
        """p > f word-initially before vowel (#_V) mutates pater to fater."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "t", "k", "s", "m", "n"]
        rules = ["p > f / #_V"]
        self.assertEqual(mutate_text("pater", rules, vowels, consonants), "fater")
        self.assertEqual(mutate_text("apater", rules, vowels, consonants), "apater")

    def test_sound_change_whole_word(self) -> None:
        """e > a in single-character word (#_#) shifts isolated word."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k"]
        rules = ["e > a / #_#"]
        self.assertEqual(mutate_text("e", rules, vowels, consonants), "a")
        self.assertEqual(mutate_text("ee", rules, vowels, consonants), "ee")

    def test_sound_change_consonant_cluster_context(self) -> None:
        """p > f after consonant before end of word (C_#) shifts kasp to kasf."""
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f", "s", "t", "k"]
        rules = ["p > f / C_#"]
        self.assertEqual(mutate_text("kasp", rules, vowels, consonants), "kasf")
        self.assertEqual(mutate_text("kap", rules, vowels, consonants), "kap")

    def test_sound_change_invalid_rule(self) -> None:
        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "f"]
        # No '>'
        fn1 = compile_sound_rule("p f", vowels, consonants)
        self.assertEqual(fn1("p"), "p")
        # Invalid regex in environment
        fn2 = compile_sound_rule("p > f / _(?", vowels, consonants)
        self.assertEqual(fn2("p"), "p")

    def test_lexicon_csv_export_and_filtering(self) -> None:
        """Lexicon entries can be filtered by query and written to standard CSV format."""
        (self.lang_dir / "Ancient.md").write_text("""---
name: "Ancient"
---
# Ancient
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Sol* | Noun | /soʊl/ | Sun | Deity |
| *Luna* | Noun | /ˈluː.nə/ | Moon | Magic |
""", encoding="utf-8")

        profile = load_conlang_profile(self.world_dir, "Ancient")
        lex = profile["lexicon"]
        filtered = [e for e in lex if "sun" in e["translation"].lower()]
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["word"], "Sol")

        csv_file = Path(self.temp_dir.name) / "lex.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["word", "pos", "ipa", "translation", "connotation"])
            writer.writeheader()
            writer.writerows(lex)

        self.assertTrue(csv_file.is_file())
        with open(csv_file, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 2)
            self.assertEqual(reader[0]["word"], "Sol")

    def test_family_tree(self) -> None:
        (self.lang_dir / "Proto.md").write_text("""---
name: "Proto-Elven"
---
""", encoding="utf-8")
        (self.lang_dir / "High_Elven.md").write_text("""---
name: "High Elven"
proto_language: "Proto-Elven"
---
""", encoding="utf-8")

        langs = load_all_conlangs(self.world_dir)
        self.assertIn("Proto-Elven", langs)
        self.assertIn("High Elven", langs)
        self.assertEqual(langs["High Elven"]["proto_language"], "Proto-Elven")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            print_family_tree(langs, "Proto-Elven")
            self.assertIn("Proto-Elven", mock_out.getvalue())
            self.assertIn("High Elven", mock_out.getvalue())

    def test_cli_all_commands(self) -> None:
        (self.lang_dir / "Old_Tongue.md").write_text("""---
name: "Old Tongue"
consonants: [p, t, k, m, n, s]
vowels: [a, e, i, o, u]
syllable_structures: ["CV", "CVC"]
sound_changes:
  - "p > f / V_V"
---
# Old Tongue
## 3. Essential Lexicon & Vocabulary
| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |
| :--- | :--- | :--- | :--- | :--- |
| *Pata* | Noun | /pa.ta/ | Father | Ancestor |
| *Mata* | Noun | /ma.ta/ | Mother | Life |
""", encoding="utf-8")

        # 1. primer
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "primer"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Beginner Conlanging Primer", mock_out.getvalue())

        # 2. no args
        with patch("sys.argv", ["conlang.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

        # 3. generate (json and text)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "generate", "Old Tongue", "-w", str(self.world_dir), "--count", "5", "--seed", "42", "--json"]):
                main()
                data = json.loads(mock_out.getvalue())
                self.assertEqual(len(data["words"]), 5)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "generate", "Old Tongue", "-w", str(self.world_dir), "--count", "3"]):
                main()
                self.assertIn("Conlang Generator: Old Tongue", mock_out.getvalue())

        # 4. mutate (json and text)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "mutate", "Old Tongue", "apata", "-w", str(self.world_dir), "--json"]):
                main()
                data = json.loads(mock_out.getvalue())
                self.assertEqual(data["mutated"], "afata")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "mutate", "Old Tongue", "-w", str(self.world_dir), "--text", "pata apata", "-r", "t > s / _#"]):
                main()
                self.assertIn("Sound-Change Mutation", mock_out.getvalue())

        # 5. lexicon (json, markdown, csv, table, query)
        csv_out = Path(self.temp_dir.name) / "lex_export.csv"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "lexicon", "Old Tongue", "-w", str(self.world_dir), "--export-csv", str(csv_out)]):
                main()
                self.assertTrue(csv_out.is_file())

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "lexicon", "Old Tongue", "-w", str(self.world_dir), "--json"]):
                main()
                data = json.loads(mock_out.getvalue())
                self.assertEqual(data["count"], 2)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "lexicon", "Old Tongue", "-w", str(self.world_dir), "--markdown"]):
                main()
                self.assertIn("| Foreign Word |", mock_out.getvalue())

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "lexicon", "Old Tongue", "-w", str(self.world_dir), "-q", "father"]):
                main()
                self.assertIn("Pata", mock_out.getvalue())

        # 6. family-tree (json and text)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "family-tree", "-w", str(self.world_dir), "--json"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                data = json.loads(mock_out.getvalue())
                self.assertIn("languages", data)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["conlang.py", "family-tree", "-w", str(self.world_dir), "-r", "Old Tongue"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Old Tongue", mock_out.getvalue())

        # 7. Invalid world dir
        with patch("sys.stderr", new_callable=io.StringIO):
            with patch("sys.argv", ["conlang.py", "lexicon", "Old Tongue", "-w", str(Path(self.temp_dir.name) / "nonexistent")]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
