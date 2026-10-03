#!/usr/bin/env python3
"""
Fuzz and Robustness Test Suite for Ars Arcanum Conlang & Historical Linguistics Engine
(tests/test_fuzz_conlang.py)
================================================================================
"""

import random
import string
import unittest

from scripts.lib.conlang import (
    compile_sound_rule,
    generate_conjugation_matrix,
    generate_declension_table,
    generate_grammar_profile,
    generate_words,
    model_semantic_shift,
    mutate_text,
)


class TestConlangFuzz(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = random.Random(42)

    def random_string(self, length: int = 10) -> str:
        chars = string.ascii_letters + string.digits + " äöüéèêñçßøåæ " + "!@#$%^&*()_+=-~`"
        return "".join(self.rng.choice(chars) for _ in range(length))

    def test_fuzz_word_generation_empty_and_corrupt_phonotactics(self) -> None:
        """Fuzzes word generation with empty, malformed, and extreme phonotactics."""
        for _ in range(50):
            consonants = [self.random_string(self.rng.randint(1, 3)) for _ in range(self.rng.randint(1, 5))]
            vowels = [self.random_string(self.rng.randint(1, 2)) for _ in range(self.rng.randint(1, 4))]
            syllables = ["CV", "CVC", "V", "VC"]

            profile = {
                "name": "FuzzLang",
                "consonants": consonants,
                "vowels": vowels,
                "syllable_structures": syllables,
                "forbidden_clusters": [],
                "stress_rule": "penultimate",
            }

            try:
                words = generate_words(
                    lang_profile=profile,
                    count=3,
                    num_syllables=2,
                )
                self.assertIsInstance(words, list)
            except Exception as e:
                self.fail(f"generate_words crashed with random phonotactics: {e}")

    def test_fuzz_sound_rule_compilation_and_mutation(self) -> None:
        """Fuzzes sound change pipeline with random and malformed rule strings."""
        sample_rules = [
            "k > ch / _[e,i]",
            "p > f / V_V",
            "s > h / #_",
            "a > o",
            "e > 0 / _#",
            "invalid_rule_syntax_without_arrow",
            "a > b / invalid[",
        ]

        vowels = ["a", "e", "i", "o", "u"]
        consonants = ["p", "t", "k", "b", "d", "g", "s", "h", "m", "n"]

        compiled_rules = []
        for r in sample_rules:
            try:
                rule = compile_sound_rule(r, vowels, consonants)
                if rule is not None:
                    compiled_rules.append(rule)
            except Exception as e:
                self.fail(f"compile_sound_rule crashed on '{r}': {e}")

        test_texts = [self.random_string(15) for _ in range(20)] + ["kethar", "valap", "solar", ""]
        for text in test_texts:
            try:
                mutated = mutate_text(text, sample_rules, vowels, consonants)
                self.assertIsInstance(mutated, str)
            except Exception as e:
                self.fail(f"mutate_text crashed on text '{text}': {e}")

    def test_fuzz_declension_table(self) -> None:
        """Fuzzes declension matrix builder with unusual root words and alignments."""
        roots = ["", "k", "valar", "123", "   ", "múspell", "!!!", "thal'khor"]
        alignments = ["Nominative-Accusative", "Ergative-Absolutive", "Tripartite", "Active-Stative", "unknown-alignment", ""]

        for root in roots:
            for alignment in alignments:
                profile = {"name": "FuzzLang", "alignment": alignment, "vowels": ["a", "i", "u"], "consonants": ["t", "k", "s"]}
                try:
                    matrix = generate_declension_table(profile, root)
                    self.assertIsInstance(matrix, dict)
                    self.assertIn("cases", matrix)
                except Exception as e:
                    self.fail(f"generate_declension_table crashed on root '{root}' and alignment '{alignment}': {e}")

    def test_fuzz_verb_conjugation_matrix(self) -> None:
        """Fuzzes verb conjugation matrix with arbitrary root stems."""
        roots = ["", "drac", "sol", "a", "xyz", "t'k", "run-fast", "   "]
        for root in roots:
            profile = {"name": "FuzzLang", "vowels": ["e", "o"], "consonants": ["r", "n", "m"]}
            try:
                matrix = generate_conjugation_matrix(profile, root)
                self.assertIsInstance(matrix, dict)
                self.assertIn("conjugations", matrix)
            except Exception as e:
                self.fail(f"generate_conjugation_matrix crashed on root '{root}': {e}")

    def test_fuzz_semantic_shift_simulation(self) -> None:
        """Fuzzes historical semantic shift with boundary epochs and random seed terms."""
        terms = ["solar", "void", "blood", "iron", "shadow", "", "custom-term-123"]
        epochs_list = [0, 1, 2, 5, 20, 100]

        for term in terms:
            for ep in epochs_list:
                try:
                    drift = model_semantic_shift(term, "meaning of " + term, epochs=ep, seed=42)
                    self.assertIsInstance(drift, dict)
                    self.assertEqual(len(drift["trajectory"]), ep + 1)
                except Exception as e:
                    self.fail(f"model_semantic_shift crashed on term '{term}' for {ep} epochs: {e}")

    def test_fuzz_grammar_profile(self) -> None:
        """Fuzzes grammar profile synthesis with arbitrary word orders and morphologies."""
        for _ in range(20):
            word_order = self.random_string(4)
            morphology = self.random_string(6)
            profile = {
                "name": "RandomLang",
                "word_order": word_order,
                "morphology": morphology,
                "alignment": "Nominative-Accusative",
            }
            try:
                synth = generate_grammar_profile(profile)
                self.assertIsInstance(synth, dict)
                self.assertIn("word_order", synth)
                self.assertIn("phrase_rules", synth)
            except Exception as e:
                self.fail(f"generate_grammar_profile crashed: {e}")


if __name__ == "__main__":
    unittest.main()
