#!/usr/bin/env python3
"""
Ars Arcanum Conlang Phonotactics, Lexicography & Sound-Change Engine (scripts/lib/conlang.py)
===========================================================================================
Local-first linguistic generator, historical sound-shift applier, and lexicon management
tool for fictional constructed languages (conlangs).

Inspects `Languages/<Lang>.md`:
- Frontmatter: consonants, vowels, syllable structures, forbidden clusters, stress rules, sound changes
- Lexicon tables: Foreign Word, Part of Speech, Pronunciation, Translation, Cultural Connotation

Capabilities:
1. Phonotactically Valid Word & Name Generator:
   - Evaluates syllable templates (e.g. CV, CVC, CCV, V, VC)
   - Enforces consonant/vowel inventories and ban-lists on invalid phonetic clusters
2. Historical Sound Shift Rule Applier (Sound Law Engine):
   - Standard notation: A > B / X_Y (e.g. 'p > f / V_V', 'k > ch / _[e,i]', 's > h / #_', 'e > 0 / _#')
3. Lexicon Management & Vocabulary Auditor:
   - Parses, searches, and exports vocabulary tables to CSV, Markdown, or JSON

Zero external runtime dependencies; 100% offline privacy.
"""

import argparse
import csv
import json
import logging
import random
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

try:
    import lib._bootstrap  # noqa: F401
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_world_scope,
        parse_scope_args,
        resolve_world_path,
    )
except ImportError:
    try:
        import _bootstrap  # noqa: F401
        from scope import (
            EngineScope,
            add_scope_arguments,
            filter_world_scope,
            parse_scope_args,
            resolve_world_path,
        )
    except ImportError:
        EngineScope = None  # type: ignore

        def add_scope_arguments(*args, **kwargs):  # type: ignore
            pass

        def parse_scope_args(*args, **kwargs):  # type: ignore
            return None

        def filter_world_scope(*args, **kwargs):  # type: ignore
            return []

        def resolve_world_path(*args, **kwargs):  # type: ignore
            return None

logger = logging.getLogger("arcanum.conlang")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)

DEFAULT_CONSONANTS = ["p", "t", "k", "b", "d", "g", "m", "n", "s", "z", "l", "r", "w", "j", "th", "sh", "ch"]
DEFAULT_VOWELS = ["a", "e", "i", "o", "u"]
DEFAULT_SYLLABLES = ["CV", "CVC", "V", "VC"]


try:
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from frontmatter import parse_yaml_frontmatter


def load_conlang_profile(world_dir: Path, lang_query: str, scope: EngineScope | None = None) -> dict:
    """Loads language definition note from Languages/ matching query name."""
    dirs_to_check = [
        world_dir / "Languages",
        world_dir / "00-World-Bible" / "Languages",
    ]
    matched_file = None
    q_clean = lang_query.strip().lower()
    q_norm = re.sub(r"[^a-z0-9]", "", q_clean)

    scoped_files: set[Path] | None = None
    if scope and scope.is_scoped():
        filtered_items = filter_world_scope(world_dir, scope)
        scoped_files = {item.file_path.resolve() for item in filtered_items}

    for ldir in dirs_to_check:
        if not ldir.is_dir():
            continue
        for md_file in sorted(ldir.rglob("*.md")):
            if "Template" in md_file.name:
                continue
            if scoped_files is not None and md_file.resolve() not in scoped_files:
                continue
            stem_norm = re.sub(r"[^a-z0-9]", "", md_file.stem.lower())
            if q_norm in stem_norm or q_clean in md_file.stem.lower().replace("_", " "):
                matched_file = md_file
                break
            # Also check frontmatter name
            try:
                txt = md_file.read_text(encoding="utf-8", errors="replace")
                fm_temp = parse_yaml_frontmatter(txt)
                if fm_temp.get("name") and q_clean in fm_temp["name"].lower():
                    matched_file = md_file
                    break
            except Exception:
                pass
        if matched_file:
            break

    if not matched_file:
        raise FileNotFoundError(f"No language note found matching '{lang_query}' in {world_dir}")

    content = matched_file.read_text(encoding="utf-8", errors="replace")
    fm = parse_yaml_frontmatter(content)

    # Phoneme inventories
    consonants = fm.get("consonants") or DEFAULT_CONSONANTS
    if isinstance(consonants, str):
        consonants = [c.strip() for c in consonants.split(",") if c.strip()]

    vowels = fm.get("vowels") or DEFAULT_VOWELS
    if isinstance(vowels, str):
        vowels = [v.strip() for v in vowels.split(",") if v.strip()]

    syllables = fm.get("syllable_structures") or fm.get("syllables") or DEFAULT_SYLLABLES
    if isinstance(syllables, str):
        syllables = [s.strip() for s in syllables.split(",") if s.strip()]

    forbidden = fm.get("forbidden_clusters") or fm.get("banned_clusters") or []
    if isinstance(forbidden, str):
        forbidden = [f.strip() for f in forbidden.split(",") if f.strip()]

    sound_changes = fm.get("sound_changes") or fm.get("mutation_rules") or []
    if isinstance(sound_changes, str):
        sound_changes = [sc.strip() for sc in sound_changes.split(";") if sc.strip()]

    # Extract Lexicon table from markdown
    lexicon = []
    if "## 3. Essential Lexicon & Vocabulary" in content or "## Lexicon" in content:
        table_lines = []
        capture = False
        for line in content.splitlines():
            if "## 3. Essential Lexicon" in line or "## Lexicon" in line:
                capture = True
                continue
            if capture:
                if line.startswith("## ") or (line.startswith("---") and len(table_lines) > 2):
                    break
                if "|" in line:
                    table_lines.append(line)

        for row in table_lines[2:]:  # skip header and divider
            cols = [c.strip().strip("*") for c in row.split("|")[1:-1]]
            if len(cols) >= 4 and cols[0]:
                lexicon.append({
                    "word": cols[0],
                    "pos": cols[1] if len(cols) > 1 else "",
                    "ipa": cols[2] if len(cols) > 2 else "",
                    "translation": cols[3] if len(cols) > 3 else "",
                    "connotation": cols[4] if len(cols) > 4 else "",
                })

    return {
        "file": str(matched_file.relative_to(world_dir)).replace("\\", "/"),
        "name": fm.get("name") or matched_file.stem,
        "proto_language": fm.get("proto_language") or fm.get("parent"),
        "language_family": fm.get("language_family") or fm.get("family"),
        "consonants": consonants,
        "vowels": vowels,
        "syllable_structures": syllables,
        "forbidden_clusters": forbidden,
        "stress_rule": fm.get("stress_rule", "penultimate"),
        "sound_changes": sound_changes,
        "lexicon": lexicon,
    }

def load_all_conlangs(world_dir: Path, scope: EngineScope | None = None) -> dict:
    """Loads all language profiles to build a family tree registry."""
    dirs_to_check = [
        world_dir / "Languages",
        world_dir / "00-World-Bible" / "Languages",
    ]
    scoped_files: set[Path] | None = None
    if scope and scope.is_scoped():
        filtered_items = filter_world_scope(world_dir, scope)
        scoped_files = {item.file_path.resolve() for item in filtered_items}

    langs = {}
    for ldir in dirs_to_check:
        if not ldir.is_dir():
            continue
        for md_file in ldir.rglob("*.md"):
            if "Template" in md_file.name:
                continue
            if scoped_files is not None and md_file.resolve() not in scoped_files:
                continue
            try:
                prof = load_conlang_profile(world_dir, md_file.stem, scope=scope)
                langs[prof["name"]] = prof
            except Exception:
                pass
    return langs

def print_family_tree(langs: dict, root_name: str, prefix: str = "", visited: set | None = None):
    """Recursively prints the language family tree."""
    if visited is None:
        visited = set()
    if root_name in visited or root_name not in langs:
        return
    visited.add(root_name)
    print(f"{prefix}\033[1;36m{root_name}\033[0m")

    children = [name for name, p in langs.items() if p.get("proto_language") == root_name]
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        sub_prefix = prefix + (" └── " if is_last else " ├── ")
        next_prefix = prefix + ("     " if is_last else " │   ")
        print(f"{sub_prefix}", end="")
        print_family_tree(langs, child, next_prefix, visited)



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


def generate_words(lang_profile: dict, count: int = 10, num_syllables: int = 2,
                   word_type: str = "word", seed: int | None = None) -> list:
    """Generates phonotactically legal words or names according to the conlang rules."""
    rng = random.Random(seed) if seed is not None else random.Random()
    consonants = lang_profile.get("consonants") or DEFAULT_CONSONANTS
    vowels = lang_profile.get("vowels") or DEFAULT_VOWELS
    syllables = lang_profile.get("syllable_structures") or DEFAULT_SYLLABLES
    forbidden = lang_profile.get("forbidden_clusters") or []

    results = []
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
        def _repl_b(m):
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
        res = []
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


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def resolve_world_dir(target_str: str | None = None, scope: EngineScope | None = None) -> str:
    """Resolves world input string (path or name) to absolute directory path."""
    if not target_str and scope and scope.world:
        target_str = scope.world

    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for u_dir in sorted((home / "Universes").glob("*/*")):
            if u_dir.is_dir() and u_dir.name.lower() == target_str.lower():
                return str(u_dir)
        for w_dir in sorted((home / "Worlds").glob("*")):
            if w_dir.is_dir() and w_dir.name.lower() == target_str.lower():
                return str(w_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    universes = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and p.name not in ("Worlds", ".git")]
    if len(universes) == 1:
        return str(universes[0])
    if len(universes) > 1:
        print("Error: Multiple worlds discovered — specify one with -w/--world.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        if len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one with -w/--world.", file=sys.stderr)
            sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Conlang Phonotactics & Sound Law Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Conlang subcommands")

    # 1. generate
    p_gen = subparsers.add_parser("generate", help="Generate phonotactically legal words, names or places")
    p_gen.add_argument("language", help="Language name (matches Languages/<Lang>.md)")
    p_gen.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_gen.add_argument("-n", "--count", type=int, default=10, help="Number of items to generate (default: 10)")
    p_gen.add_argument("-s", "--syllables", type=int, default=2, help="Number of syllables (default: 2)")
    p_gen.add_argument("-t", "--type", choices=["word", "name", "place"], default="name", help="Type of generation")
    p_gen.add_argument("--seed", type=int, help="Optional deterministic random seed")
    p_gen.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_gen, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 2. mutate
    p_mut = subparsers.add_parser("mutate", help="Apply historical sound changes and phonological shifts")
    p_mut.add_argument("language", help="Language name")
    p_mut.add_argument("input", nargs="?", help="Word or text string to mutate")
    p_mut.add_argument("--text", help="Text passage to mutate")
    p_mut.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_mut.add_argument("-r", "--rule", action="append", help="Ad-hoc sound change rule (e.g. 'p > f / V_V')")
    p_mut.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_mut, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 3. lexicon
    p_lex = subparsers.add_parser("lexicon", help="Inspect and search language lexicon table")
    p_lex.add_argument("language", help="Language name")
    p_lex.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_lex.add_argument("-q", "--query", help="Search word or English translation")
    p_lex.add_argument("--export-csv", help="Export lexicon to CSV file")
    p_lex.add_argument("--markdown", action="store_true", help="Print as Markdown table")
    p_lex.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_lex, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 4. family-tree
    p_fam = subparsers.add_parser("family-tree", help="Display proto-language family tree registry")
    p_fam.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_fam.add_argument("-r", "--root", help="Root language to display tree for (optional)")
    p_fam.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_fam, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 5. grammar
    p_gram = subparsers.add_parser("grammar", help="Synthesize word-order typology, morphology, and phrase structure")
    p_gram.add_argument("language", help="Language name")
    p_gram.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_gram.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_gram, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 6. declension
    p_dec = subparsers.add_parser("declension", help="Generate regular noun case declension tables")
    p_dec.add_argument("language", help="Language name")
    p_dec.add_argument("noun", help="Base noun stem to decline")
    p_dec.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_dec.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_dec, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 7. conjugate
    p_conj = subparsers.add_parser("conjugate", help="Generate regular verb conjugation paradigm across tenses & moods")
    p_conj.add_argument("language", help="Language name")
    p_conj.add_argument("verb", help="Verb root/stem to conjugate")
    p_conj.add_argument("-w", "--world", "--world-dir", dest="world_flag", help="World Bible lore directory")
    p_conj.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_conj, include_manuscript=False, include_world=False, target_pos_arg=False)

    # 8. semantic-shift
    p_sem = subparsers.add_parser("semantic-shift", help="Model historical semantic drift and meaning shift across epochs")
    p_sem.add_argument("word", help="Target word or vocabulary item")
    p_sem.add_argument("meaning", help="Original definition or semantic gloss")
    p_sem.add_argument("-e", "--epochs", type=int, default=3, help="Number of simulated historical epochs (default: 3)")
    p_sem.add_argument("--seed", type=int, help="Deterministic random seed")
    p_sem.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 9. primer
    subparsers.add_parser("primer", help="Show comprehensive beginner conlanging primer")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "primer":
        print("\n\033[1;36m=== Beginner Conlanging Primer ===\033[0m")
        print("Welcome to Ars Arcanum's Conlanging Engine!")
        print("1. **Phonotactics**: Syllable structures like CV, CVC define how sounds combine.")
        print("2. **Inventories**: The consonant and vowel charts define the basic sounds of your language.")
        print("3. **Sound Shifts**: Historical changes follow the format 'A > B / X_Y', meaning 'A becomes B when preceded by X and followed by Y'.")
        print("   - Example: 'p > f / V_V' (p becomes f between two vowels).")
        print("4. **Language Families**: Define 'proto_language: Name' in your YAML frontmatter to build a family tree.")
        print("Use the 'generate', 'mutate', and 'lexicon' commands to play with your language.")
        sys.exit(0)

    # Discover world
    if args.subcommand == "semantic-shift":
        shift_res = model_semantic_shift(args.word, args.meaning, epochs=args.epochs, seed=args.seed)
        if args.json:
            print(json.dumps(shift_res, indent=2))
        else:
            print(f"\n\033[1;36m=== Historical Semantic Shift Simulation: '{args.word}' ===\033[0m")
            print(f"Original Root Meaning: \033[33m{args.meaning}\033[0m | Simulated Epochs: \033[32m{args.epochs}\033[0m\n")
            for step in shift_res["trajectory"]:
                print(f"  \033[1m{step['epoch']:<30}\033[0m -> \033[1;32m{step['meaning']:<30}\033[0m \033[90m[{step['shift_type']}]\033[0m")
            print()
        sys.exit(0)

    scope = parse_scope_args(args)
    raw_w = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir = resolve_world_dir(raw_w, scope=scope)

    if not world_dir or not Path(world_dir).is_dir():
        print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
        sys.exit(2)

    try:
        if args.subcommand == "family-tree":
            langs = load_all_conlangs(Path(world_dir), scope=scope)
            if args.json:
                print(json.dumps({"languages": langs}, indent=2))
            else:
                print("\n\033[1;36m=== Language Family Trees ===\033[0m\n")
                if args.root:
                    if args.root in langs:
                        print_family_tree(langs, args.root)
                    else:
                        print(f"Language '{args.root}' not found.")
                else:
                    roots = [name for name, p in langs.items() if not p.get("proto_language")]
                    for root in roots:
                        print_family_tree(langs, root)
                        print()
            sys.exit(0)

        profile = load_conlang_profile(Path(world_dir), args.language, scope=scope)

        if args.subcommand == "generate":
            generated = generate_words(
                profile,
                count=args.count,
                num_syllables=args.syllables,
                word_type=args.type,
                seed=args.seed
            )
            if args.json:
                print(json.dumps({
                    "language": profile["name"],
                    "type": args.type,
                    "syllables": args.syllables,
                    "words": generated
                }, indent=2))
            else:
                print(f"\n\033[1;36m=== Conlang Generator: {profile['name']} ===\033[0m")
                print(f"Syllable Structures: \033[32m{', '.join(profile['syllable_structures'])}\033[0m | Stress: \033[33m{profile['stress_rule']}\033[0m")
                print(f"Generated {args.count} {args.type}s:\n")
                for w in generated:
                    print(f"  ✨ \033[1m{w}\033[0m")
                print()

        elif args.subcommand == "mutate":
            target_text = args.input or args.text or ""
            rules = args.rule or profile.get("sound_changes", [])
            if not rules:
                print("Note: No sound-change rules defined in language note or --rule arguments.", file=sys.stderr)

            mutated = mutate_text(target_text, rules, profile["vowels"], profile["consonants"])

            if args.json:
                print(json.dumps({
                    "language": profile["name"],
                    "original": target_text,
                    "mutated": mutated,
                    "rules_applied": rules
                }, indent=2))
            else:
                print(f"\n\033[1;36m=== Sound-Change Mutation: {profile['name']} ===\033[0m")
                print(f"Rules Applied: \033[33m{'; '.join(rules) if rules else 'None'}\033[0m\n")
                print(f"  Original: \033[90m{target_text}\033[0m")
                print(f"  Shifted:  \033[1;32m{mutated}\033[0m\n")

        elif args.subcommand == "lexicon":
            lex = profile.get("lexicon", [])
            if args.query:
                q = args.query.lower()
                lex = [entry for entry in lex if q in entry["word"].lower() or q in entry["translation"].lower() or q in entry.get("connotation", "").lower()]

            if args.export_csv:
                csv_path = Path(args.export_csv)
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["word", "pos", "ipa", "translation", "connotation"])
                    writer.writeheader()
                    writer.writerows(lex)
                print(f"Exported {len(lex)} lexicon entries to: {csv_path}")

            elif args.json:
                print(json.dumps({"language": profile["name"], "count": len(lex), "lexicon": lex}, indent=2))
            elif args.markdown:
                print("\n| Foreign Word | Part of Speech | Pronunciation | English Translation | Cultural Connotation |")
                print("| :--- | :--- | :--- | :--- | :--- |")
                for e in lex:
                    print(f"| *{e['word']}* | {e['pos']} | {e['ipa']} | {e['translation']} | {e['connotation']} |")
            else:
                print(f"\n\033[1;36m=== Conlang Lexicon: {profile['name']} ({len(lex)} Entries) ===\033[0m\n")
                for e in lex:
                    print(f"  \033[1;32m{e['word']:<14}\033[0m \033[90m[{e['pos']}]\033[0m \033[36m{e['ipa']:<12}\033[0m -> \033[1m{e['translation']}\033[0m \033[33m({e['connotation']})\033[0m")
                print()

        elif args.subcommand == "grammar":
            gram = generate_grammar_profile(profile)
            if args.json:
                print(json.dumps(gram, indent=2))
            else:
                print(f"\n\033[1;36m=== Conlang Morphosyntax & Grammar: {profile['name']} ===\033[0m")
                print(f"Word Order: \033[1;32m{gram['word_order']}\033[0m | Morphology: \033[33m{gram['morphology']}\033[0m | Alignment: \033[35m{gram['alignment']}\033[0m")
                print(f"Directionality: \033[36m{gram['head_direction']}\033[0m\n")
                print("Phrase Structure Rules:")
                for rule_k, rule_v in gram["phrase_rules"].items():
                    print(f"  • {rule_k.replace('_', ' ').title():<20} -> \033[1m{rule_v}\033[0m")
                ex = gram["example_sentence"]
                print(f"\nSample Sentence Construction ({gram['word_order']}):")
                print(f"  Text:        \033[1;32m{ex['text']}\033[0m")
                print(f"  Gloss:       \033[90m{ex['gloss']}\033[0m")
                print(f"  Translation: \033[33m{ex['translation']}\033[0m\n")

        elif args.subcommand == "declension":
            decl = generate_declension_table(profile, args.noun)
            if args.json:
                print(json.dumps(decl, indent=2))
            else:
                print(f"\n\033[1;36m=== Noun Case Declension Table: {profile['name']} ('{args.noun}') ===\033[0m")
                print(f"Alignment: \033[35m{decl['alignment']}\033[0m\n")
                print(f"  {'Case':<18} | {'Singular':<16} | {'Plural':<16} | {'Dual':<16}")
                print("  " + "-" * 72)
                for c in decl["cases"]:
                    print(f"  {c['case']:<18} | \033[1;32m{c['singular']:<16}\033[0m | \033[33m{c['plural']:<16}\033[0m | \033[36m{c['dual']:<16}\033[0m")
                print()

        elif args.subcommand == "conjugate":
            conj = generate_conjugation_matrix(profile, args.verb)
            if args.json:
                print(json.dumps(conj, indent=2))
            else:
                print(f"\n\033[1;36m=== Verb Conjugation Paradigm: {profile['name']} ('{args.verb}') ===\033[0m\n")
                print(f"  {'Person / Number':<24} | {'Present':<14} | {'Past':<14} | {'Future':<14} | {'Subjunctive':<14}")
                print("  " + "-" * 88)
                for row in conj["conjugations"]:
                    print(f"  {row['person']:<24} | \033[1;32m{row['present']:<14}\033[0m | \033[33m{row['past']:<14}\033[0m | \033[36m{row['future']:<14}\033[0m | \033[35m{row['subjunctive']:<14}\033[0m")
                print()

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


