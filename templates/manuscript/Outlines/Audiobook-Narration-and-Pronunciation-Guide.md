# Audiobook Narration, Phonetic Guide & SSML Prosody Specification
### Professional Voice Actor Briefing & Acoustic Proofing Pipeline in Ars Arcanum

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original audiobook production and pronunciation data.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Specification:
- **Audiobook Proofing & Phonetic Pipeline**: `audio_proof` (`arcanum audio-proof Manuscripts/Book-01`) — Synthesizes acoustic SSML markup, word cadence distributions, and listening timing estimation.
- **SSML Prosody Optimization**: `audio_proof` (`arcanum audio-proof --ssml`) — Calibrates prosodic rate, pitch modulation, and dialogue pause durations.
- **Chunked TTS Buffer Exporter**: `audio_proof` (`arcanum audio-proof --chunk 500`) — Chunks manuscripts into deterministic buffers for offline Piper / eSpeak NG TTS synthesis.
- **Narration Duration Estimator**: `audio_proof` (`arcanum audio-proof --estimate`) — Computes exact finished audio hours based on a standard 155 words-per-minute commercial narration pace.
- **Conlang IPA Harmonizer**: Links directly with `conlang` (`Languages/Glossary-Conlang-Template.md`) to provide International Phonetic Alphabet (IPA) guidance for voice talent.

### How to Use for Your Projects:
1. Populate the Phonetic Pronunciation Lexicon for all proper nouns, character names, and spell incantations.
2. Provide character voice notes (pitch, accent, vocal fry, pacing) for the audio narrator.
3. Use the SSML markup templates to proof chapter rhythm acoustically with offline TTS before hiring voice talent.
</details>

> *"The eye forgives what the ear condemns; read your prose aloud, or let the machine whisper it back to you."*

---

## 1. Production Metrics & Total Listening Duration Forecast

```
[Manuscript Word Count: 95,000 Words]
  └── Standard Narration Velocity: 155 Words Per Minute (WPM)
  └── Total Unedited Audio Runtime: ~10.2 Hours (612 Minutes)
  └── Mastered Audio Book Size: ~560 MB (192 kbps MP3 Standard)
```

| Dimension | Target Specification | Production Standard |
| :--- | :--- | :--- |
| **Pacing / Speed** | `150 – 160 WPM` | Standard commercial ACX / Audible cadence. |
| **Room Tone / Silence** | `0.75s – 1.0s` between paragraphs; `3.0s` between chapters | ACX Head/Tail room noise floor (< -60 dB). |
| **Dialogue Modulation** | +5% pitch for high tension; -10% rate for solemn oaths | Dynamic SSML prosody ranges. |

---

## 2. Character Vocal Profiles & Voice Talent Direction

| Character | Accent / Regional Dialect | Pitch & Timbre | Mannerisms & Cadence Notes | Sample Opening Line |
| :--- | :--- | :--- | :--- | :--- |
| **Narrator (Third Person)** | Neutral Transatlantic / BBC Received Pronunciation | Warm Baritone, crisp consonants | Steady, authoritative, measured pacing; accelerates slightly during action. | *"The third seal was cold as winter iron when Kaelen touched the lead."* |
| [[Characters/Character-Template\|Kaelen (Protagonist)]] | Highland Northern | Low Tenor, dry, gravelly edge | Analytical, terse, clipped sentence endings; habitual mid-sentence pauses when calculating odds. | *"Step back, or I will let the aether cannons calculate the difference."* |
| [[Characters/Character-Template\|Aeloria-Vael]] | Coastal Basin Vernacular | Lyrical Alto, rapid and melodic | Fluid, sharp, sardonic wit; upward inflection on rhetorical questions. | *"You scholars always count the stones while the roof is caving in."* |
| [[Characters/Character-Template\|Archmage-Theron]] | Ancient High Imperial | Deep Bass, resonant, slow | Gravitas; resonant chest timbre; deliberate 1.5s pauses between key injunctions. | *"In ferro veritas, in aether salus. Remember your vows, child."* |

---

## 3. Phonetic Pronunciation Master Lexicon (IPA & Phonetic Respelling)

```
=============================================================================
TERM / PROPER NOUN    IPA PRONUNCIATION    AUDIO RESPEL        MEANING / CONTEXT
=============================================================================
Aethelgard            /ˈeɪ.θəl.ɡɑːrd/      AY-thəl-gard        The primary continent
Kaelen                /ˈkeɪ.lən/           KAY-lən             Protagonist inquisitor
Aeloria               /eɪ.ˈlɔː.ri.ə/       ay-LOR-ee-uh        Highland scout / smuggler
Theron                /ˈθɛ.rɒn/            THEH-ron            Grand Inquisitor
Valdoria              /væl.ˈdɔː.ri.ə/      val-DOR-ee-uh       Ancestral kingdom
Vael                  /ˈvaɪl/              VILE (rhymes)       Pure aether energy
Sil-moran             /sɪl.ˈmɔː.ræn/       sil-MOR-an          The silver night vigil
Kaelis-mor            /ˈkeɪ.lɪs.mɔːr/      KAY-lis-mor         Highland curse (cold hearth)
Vitriol               /ˈvɪt.ri.əl/         VIT-ree-ul          Arcane mineral reagent
=============================================================================
```

---

## 4. SSML (Speech Synthesis Markup Language) Formatting Prototype

For testing acoustic prosody and synthetic narration with offline engines (Piper / eSpeak NG):

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <prosody rate="medium" pitch="0%">
    <s>The ink on the treaty was dry, <break time="400ms"/> but the blood spilt to seal it was still warm.</s>
  </prosody>

  <prosody rate="-5%" pitch="-2st">
    <!-- Archmage Theron Dialogue -->
    <voice name="en_GB-southern_male">
      <s>"Step back from the gate, Commander."</s>
    </voice>
  </prosody>

  <prosody rate="+10%" pitch="+1st">
    <!-- Fast-Paced Action Narrative -->
    <s>The iron hammers struck the cedar timber with a deafening crash. <break time="200ms"/> Wood splintered. Dust boiled from the flumes.</s>
  </prosody>
</speak>
```

---

## 5. ACX / Audible Mastering Quality Gates

- [ ] All audio files exported as CBR MP3 at 192 kbps or 320 kbps (44.1 kHz, 16-bit).
- [ ] Peak levels remain strictly below **-3.0 dB**.
- [ ] RMS loudness measures between **-23 dB and -18 dB** consistently across chapters.
- [ ] Noise floor does not exceed **-60 dB RMS**.
- [ ] Each chapter file contains exactly 0.5 to 1.0 second of room tone at the start, and 1.0 to 5.0 seconds at the end.
