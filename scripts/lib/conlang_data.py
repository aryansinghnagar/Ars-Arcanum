#!/usr/bin/env python3
"""
Ars Arcanum Conlang Phonotactics, Sound Shift & Morphosyntax Primitives
(scripts/lib/conlang_data.py)
================================================================================
Zero-dependency phonetic rules, syllable generators, historical sound shift
compilers, declension/conjugation paradigm synthesizers, and semantic drift models.
"""

import logging
import random
import re
from collections.abc import Callable, Sequence

__all__ = [
    "DEFAULT_CONSONANTS",
    "DEFAULT_SYLLABLES",
    "DEFAULT_VOWELS",
    "FRONTMATTER_REGEX",
    "compile_sound_rule",
    "generate_conjugation_matrix",
    "generate_declension_table",
    "generate_grammar_profile",
    "generate_syllable",
    "generate_words",
    "model_semantic_shift",
    "mutate_text",
]

logger = logging.getLogger("arcanum.conlang")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)

DEFAULT_CONSONANTS = ["p", "t", "k", "b", "d", "g", "m", "n", "s", "z", "l", "r", "w", "j", "th", "sh", "ch"]
DEFAULT_VOWELS = ["a", "e", "i", "o", "u"]
DEFAULT_SYLLABLES = ["CV", "CVC", "V", "VC"]


# ==============================================================================
# Phonotactic Word Generation
# ==============================================================================

def generate_syllable(structure: str, consonants: list, vowels: list, rng: random.Random) -> str:
    """Generates a single syllable matching the structural pattern (e.g. 'CVC', 'CCV')."""
    syl = []
    for char in structure:
        if char == "C":
            syl.append(rng.choice(consonants))
        elif char == "V":
            syl.append(rng.choice(vowels))
        else:
            syl.append(char)
    return "".join(syl)


def generate_words(
    lang_profile: dict,
    count: int = 10,
    num_syllables: int = 2,
    word_type: str = "word",
    seed: int | None = None,
) -> list[str]:
    """Generates phonotactically legal words or names according to the conlang rules."""
    rng = random.Random(seed) if seed is not None else random.Random()
    consonants = lang_profile.get("consonants") or DEFAULT_CONSONANTS
    vowels = lang_profile.get("vowels") or DEFAULT_VOWELS
    syllables = lang_profile.get("syllable_structures") or DEFAULT_SYLLABLES
    forbidden = lang_profile.get("forbidden_clusters") or []

    results: list[str] = []
    attempts = 0
    max_attempts = count * 200

    while len(results) < count and attempts < max_attempts:
        attempts += 1
        syl_count = num_syllables
        if word_type == "name" and num_syllables == 2:
            syl_count = rng.choice([2, 3])
        elif word_type == "place":
            syl_count = rng.choice([2, 3, 4])

        syls = [generate_syllable(rng.choice(syllables), consonants, vowels, rng) for _ in range(syl_count)]
        candidate = "".join(syls)

        # Check forbidden clusters
        is_legal = True
        for fc in forbidden:
            if fc and fc in candidate:
                is_legal = False
                break

        # Check triple repeating characters
        if re.search(r"(.)\1\1", candidate):
            is_legal = False

        if is_legal:
            if word_type in ("name", "place"):
                candidate = candidate.capitalize()
            if candidate not in results:
                results.append(candidate)

    return results


# ==============================================================================
# Historical Sound-Change Applier
# ==============================================================================

def compile_sound_rule(rule_str: str, vowels: Sequence[str], consonants: Sequence[str]) -> Callable[[str], str]:
    """
    Parses linguistic sound change rule e.g. 'p > f / V_V' or 'k > ch / _[e,i]'.
    Returns a transformer function: word -> mutated_word.
    """
    rule = rule_str.strip()
    if ">" not in rule:
        return lambda w: w

    parts = rule.split(">", 1)
    source = parts[0].strip()
    target_and_env = parts[1].split("/", 1)
    target = target_and_env[0].strip()
    if target in ("0", "null", "none", "Ø"):
        target = ""

    env = target_and_env[1].strip() if len(target_and_env) > 1 else "_"

    v_set = "|".join(re.escape(v) for v in sorted(vowels, key=len, reverse=True)) if vowels else r"(?!)"
    c_set = "|".join(re.escape(c) for c in sorted(consonants, key=len, reverse=True)) if consonants else r"(?!)"

    left_env, right_env = env.split("_", 1) if "_" in env else ("", "")

    def prep_env(e_str: str, is_left: bool) -> str:
        if not e_str:
            return ""
        s = e_str
        s = s.replace("#", "^") if is_left else s.replace("#", "$")
        s = re.sub(r"(?<!\\)V", f"(?:{v_set})", s)
        s = re.sub(r"(?<!\\)C", f"(?:{c_set})", s)

        def _repl_b(m: re.Match) -> str:
            items = [re.escape(x.strip()) for x in m.group(1).split(",") if x.strip()]
            return f"(?:{'|'.join(items)})"

        return re.sub(r"\[(.*?)\]", _repl_b, s)

    left_re = prep_env(left_env, True)
    right_re = prep_env(right_env, False)

    if source == "V":
        src_re = f"(?:{v_set})"
    elif source == "C":
        src_re = f"(?:{c_set})"
    else:
        src_re = re.escape(source)

    try:
        re.compile(src_re, re.IGNORECASE)
        if left_re:
            re.compile(f"({left_re})$", re.IGNORECASE)
        if right_re:
            re.compile(f"^{right_re}", re.IGNORECASE)
    except re.error as e:
        logger.warning("Failed to compile sound change rule '%s': %s", rule_str, e)
        return lambda w: w

    def apply_rule(word: str) -> str:
        res: list[str] = []
        i = 0
        while i < len(word):
            m_src = re.match(src_re, word[i:], re.IGNORECASE)
            if m_src and len(m_src.group(0)) > 0:
                m_left = re.search(f"({left_re})$", word[:i], re.IGNORECASE) if left_re else True
                m_right = re.match(f"^{right_re}", word[i + len(m_src.group(0)):], re.IGNORECASE) if right_re else True
                if m_left and m_right:
                    res.append(target)
                    i += len(m_src.group(0))
                    continue
            res.append(word[i])
            i += 1
        return "".join(res)

    return apply_rule


def mutate_text(text: str, rules: Sequence[str], vowels: Sequence[str], consonants: Sequence[str]) -> str:
    """Applies a sequence of historical sound change rules to a word or prose text."""
    compiled_rules = [compile_sound_rule(r, vowels, consonants) for r in rules if r.strip()]

    def mutate_single_word(w: str) -> str:
        is_cap = w.istitle()
        curr = w.lower()
        for rule_fn in compiled_rules:
            curr = rule_fn(curr)
        return curr.capitalize() if is_cap else curr

    # Match words preserving punctuation and spacing (Unicode-aware word boundary)
    return re.sub(r"[^\W\d_]+(?:'[^\W\d_]+)*", lambda m: mutate_single_word(m.group(0)), text)


# ==============================================================================
# Grammar & Typology Primitives
# ==============================================================================

def _generate_example_sentence(order: str, phrase_rules: dict, profile: dict) -> dict:
    """Generates an illustrative sentence layout for the word order."""
    lexicon = profile.get("lexicon", [])
    nouns = [e for e in lexicon if e.get("pos", "").lower() in ("noun", "n")]
    verbs = [e for e in lexicon if e.get("pos", "").lower() in ("verb", "v")]

    s_word = nouns[0]["word"] if len(nouns) > 0 else "kael"
    s_gloss = nouns[0]["translation"] if len(nouns) > 0 else "hunter"
    o_word = nouns[1]["word"] if len(nouns) > 1 else (nouns[0]["word"] + "en" if len(nouns) > 0 else "dor")
    o_gloss = nouns[1]["translation"] if len(nouns) > 1 else "beast"
    v_word = verbs[0]["word"] if len(verbs) > 0 else "vath"
    v_gloss = verbs[0]["translation"] if len(verbs) > 0 else "strikes"

    tokens = []
    glosses = []
    for comp in list(order):
        if comp == "S":
            tokens.append(s_word)
            glosses.append(f"{s_gloss}.NOM")
        elif comp == "O":
            tokens.append(o_word)
            glosses.append(f"{o_gloss}.ACC")
        elif comp == "V":
            tokens.append(v_word)
            glosses.append(f"{v_gloss}.PRES")

    return {
        "text": " ".join(tokens).capitalize() + ".",
        "gloss": " ".join(glosses) + ".",
        "translation": f"The {s_gloss} {v_gloss} the {o_gloss}.",
    }


def generate_grammar_profile(profile: dict) -> dict:
    """Synthesizes word-order typology, morphological typology, and phrase structure."""
    fm = profile.get("frontmatter", {})
    word_order = str(fm.get("word_order") or profile.get("word_order") or "SVO").upper().strip()
    valid_orders = ["SOV", "SVO", "VSO", "VOS", "OVS", "OSV"]
    if word_order not in valid_orders:
        word_order = "SVO"

    morphology = str(fm.get("morphology") or profile.get("morphology") or "Agglutinative").capitalize().strip()
    valid_morph = ["Isolating", "Agglutinative", "Fusional", "Polysynthetic"]
    if morphology not in valid_morph:
        morphology = "Agglutinative"

    alignment = str(fm.get("alignment") or profile.get("alignment") or "Nominative-Accusative").strip()

    # Determine head directionality based on dominant typology
    is_head_initial = word_order in ("SVO", "VSO", "VOS")

    phrase_rules = {
        "adjective_noun": "Noun + Adjective" if is_head_initial else "Adjective + Noun",
        "genitive_noun": "Noun + Genitive (Possessor)" if is_head_initial else "Genitive (Possessor) + Noun",
        "adpositions": "Prepositions" if is_head_initial else "Postpositions",
        "relative_clause": "Noun + Relative Clause" if is_head_initial else "Relative Clause + Noun",
    }

    return {
        "language": profile.get("name", "Unknown"),
        "word_order": word_order,
        "morphology": morphology,
        "alignment": alignment,
        "head_direction": "Head-Initial" if is_head_initial else "Head-Final",
        "phrase_rules": phrase_rules,
        "example_sentence": _generate_example_sentence(word_order, phrase_rules, profile),
    }


def generate_declension_table(profile: dict, base_noun: str) -> dict:
    """Generates a regular case declension matrix for a base noun."""
    alignment = str(profile.get("alignment") or "Nominative-Accusative").strip()
    is_ergative = "ergative" in alignment.lower()

    # Deterministic affix generation based on vowel harmony / phonotactics
    vowels = profile.get("vowels") or DEFAULT_VOWELS
    consonants = profile.get("consonants") or DEFAULT_CONSONANTS
    v = vowels[0] if vowels else "a"
    c = consonants[0] if consonants else "n"

    affixes = {
        "Nom/Abs": ("", f"-{v}s", f"-{v}n"),
        "Acc/Erg": (f"-{v}{c}", f"-{v}s{c}", f"-{v}n{c}") if not is_ergative else (f"-{c}{v}", f"-{c}{v}s", f"-{c}{v}n"),
        "Genitive": (f"-{v}r", f"-{v}sr", f"-{v}nr"),
        "Dative": (f"-{v}t", f"-{v}st", f"-{v}nt"),
        "Ablative": (f"-{v}l", f"-{v}sl", f"-{v}nl"),
        "Locative": (f"-{v}m", f"-{v}sm", f"-{v}nm"),
        "Instrumental": (f"-{v}k", f"-{v}sk", f"-{v}nk"),
        "Vocative": (f"-{v}", f"-{v}e", f"-{v}o"),
    }

    cases = []
    for case_name, (sg_sfx, pl_sfx, dual_sfx) in affixes.items():
        clean_sg = sg_sfx.lstrip("-")
        clean_pl = pl_sfx.lstrip("-")
        clean_dual = dual_sfx.lstrip("-")
        cases.append({
            "case": case_name,
            "singular": f"{base_noun}{clean_sg}",
            "plural": f"{base_noun}{clean_pl}",
            "dual": f"{base_noun}{clean_dual}",
        })

    return {
        "language": profile.get("name", "Unknown"),
        "base_noun": base_noun,
        "alignment": alignment,
        "cases": cases,
    }


def generate_conjugation_matrix(profile: dict, verb_stem: str) -> dict:
    """Generates verb conjugation paradigm across tenses, aspects, and person."""
    vowels = profile.get("vowels") or DEFAULT_VOWELS
    consonants = profile.get("consonants") or DEFAULT_CONSONANTS
    v = vowels[0] if vowels else "a"
    c = consonants[0] if consonants else "r"

    persons = [
        ("1st Singular (I)", f"{v}", f"i{v}", f"e{v}"),
        ("2nd Singular (Thou/You)", f"{v}s", f"i{v}s", f"e{v}s"),
        ("3rd Singular (He/She/It)", f"{v}{c}", f"i{v}{c}", f"e{v}{c}"),
        ("1st Plural (We)", f"{v}m", f"i{v}m", f"e{v}m"),
        ("2nd Plural (You all)", f"{v}th", f"i{v}th", f"e{v}th"),
        ("3rd Plural (They)", f"{v}n", f"i{v}n", f"e{v}n"),
    ]

    paradigms = []
    for person_label, pres_sfx, past_sfx, fut_sfx in persons:
        paradigms.append({
            "person": person_label,
            "present": f"{verb_stem}{pres_sfx}",
            "past": f"{verb_stem}{past_sfx}",
            "future": f"{verb_stem}{fut_sfx}",
            "subjunctive": f"{verb_stem}al{pres_sfx}",
            "imperative": f"{verb_stem}o" if "2nd" in person_label else "-",
        })

    return {
        "language": profile.get("name", "Unknown"),
        "verb_stem": verb_stem,
        "conjugations": paradigms,
    }


def model_semantic_shift(
    word: str,
    original_meaning: str,
    epochs: int = 3,
    seed: int | None = None,
) -> dict:
    """Models historical semantic drift over simulated historical epochs."""
    rng = random.Random(seed) if seed is not None else random.Random()

    shift_types = [
        ("Pejoration (Negative specialization)", "meaning becomes derogatory or taboo", ["corrupted", "vulgar", "sinister", "petty"]),
        ("Amelioration (Elevation)", "meaning acquires noble or elevated status", ["sacred", "honored", "master", "radiant"]),
        ("Broadening (Generalization)", "meaning expands to encompass wider category", ["general", "common", "universal", "omnipresent"]),
        ("Narrowing (Specialization)", "meaning restricts to specific sub-domain", ["technical", "exclusive", "ritualistic", "elite"]),
        ("Metaphorical Transfer", "concrete physical term transfers to abstract mental concept", ["spiritual", "metaphoric", "philosophical", "psychological"]),
    ]

    history = [
        {
            "epoch": "Proto-Era (0)",
            "meaning": original_meaning,
            "shift_type": "Root Baseline",
            "connotation": "Original concrete definition",
        }
    ]

    curr_meaning = original_meaning
    for ep in range(1, epochs + 1):
        st_name, st_desc, descriptors = rng.choice(shift_types)
        desc = rng.choice(descriptors)
        curr_meaning = f"{desc} {curr_meaning}"
        history.append({
            "epoch": f"Epoch {ep} ({ep * 400} Years Later)",
            "meaning": curr_meaning,
            "shift_type": st_name,
            "connotation": st_desc,
        })

    return {
        "word": word,
        "original_meaning": original_meaning,
        "epochs_simulated": epochs,
        "trajectory": history,
    }
