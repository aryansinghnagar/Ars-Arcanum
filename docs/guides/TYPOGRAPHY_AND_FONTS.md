# Typography, Classical Proportions & Font Masterclass for Fiction (`docs/guides/TYPOGRAPHY_AND_FONTS.md`)
> **Domain B & G: Typography, Book Design & Publishing Aesthetics**

---

## 1. Overview & Typographic Philosophy

Typesetting is the invisible bridge between an author's manuscript and the reader's imagination. As Beatrice Warde argued in *The Crystal Goblet*, great typography is like a crystal wineglass: completely transparent, allowing the richness of the vintage (the story) to be experienced without visual distortion.

Professional book typography transforms raw text into an enduring physical or digital artifact through precise mathematical proportion, optical rhythm, and micro-typographic discipline.

```
+-------------------------------------------------------------------------------+
|                    THE THREE TIERS OF BOOK TYPOGRAPHY                         |
|                                                                               |
|  [Macro-Typography]  --> Page Geometry, Golden Ratio (1:1.618), Margins       |
|                                                                               |
|  [Meso-Typography]   --> Hierarchy, Heading Scales, Leading, Line Measure     |
|                                                                               |
|  [Micro-Typography]  --> Directional Quotes, Em-Dashes, Ligatures, Kerning    |
+-------------------------------------------------------------------------------+
```

---

## 2. Top Recommended Free & Open-Source Book Typefaces

| Typeface Family | Classification | Typographic Character & Aesthetic | Optimal Genre Application |
|---|---|---|---|
| **Linux Libertine / Libertinus** | Transitional Serif | Classical Roman proportions, crisp serifs, rich OpenType ligatures, robust x-height. | Universal Fiction, Contemporary, Sci-Fi |
| **EB Garamond** | Renaissance Humanist | Direct digital revival of Claude Garamont's 1592 specimen; soft, organic, timeless grace. | Literary Fiction, Historical, Epic Fantasy |
| **Alegreya** | Contemporary Humanist | Designed specifically for long continuous literature reading; lively, dynamic rhythm. | Fantasy, Adventure, Long-form Sagas |
| **Cormorant Garamond** | High-Contrast Display | Exquisite hairline serifs, dramatic tall ascenders, flowing swashes. | Title Pages, Poetry, Gothic Romances |
| **Bitter** | Contemporary Slab-Serif | Sturdy geometric serifs optimized for screen readability and e-ink displays. | Urban Fantasy, Modern Thrillers |
| **Charis SIL / Gentium Plus** | Extended Humanist | Exhaustive Unicode IPA support, phonetic diacritics, and conlang orthographies. | Linguistics, World Bibles, Conlangs |

---

## 3. Font Installation & Host Verification

### 3.1 Linux Mint / Debian / Ubuntu Font Package Installation
```bash
sudo apt update
sudo apt install -y \
  fonts-linuxlibertine \
  fonts-libertinus \
  fonts-ebgaramond \
  fonts-alegreya \
  fonts-sil-charis \
  fonts-sil-gentiumplus \
  fonts-bitter \
  fonts-cmu
```

### 3.2 Adding Custom OpenType / TrueType Fonts (`.otf` / `.ttf`)
1. Create user font directory:
   ```bash
   mkdir -p ~/.local/share/fonts
   ```
2. Copy font files into `~/.local/share/fonts/`.
3. Refresh the font cache:
   ```bash
   fc-cache -f -v
   ```
4. Verify Typst detects the installed typeface:
   ```bash
   typst fonts | grep -i "Garamond"
   ```

---

## 4. Page Geometry & Classical Proportions

```
+--------------------------------------------------------+
|  Jan Tschichold / Van de Graaf Canon (9x9 Grid)        |
|                                                        |
|  +-----------------------------+--------------------+  |
|  | Verso (Left Page)           | Recto (Right Page) |  |
|  |                             |                    |  |
|  |    +--------+ (Top: 2u)     |     (Top: 2u)      |  |
|  |    |        |               |      +--------+    |  |
|  | (3u| Text   |(1.5u)   (1.5u)| (3u) | Text   |    |  |
|  | Out| Block  |Gutter   Gutter| Out  | Block  |    |  |
|  |    |        |               |      |        |    |  |
|  |    +--------+               |      +--------+    |  |
|  |    (Bottom: 4u)             |      (Bottom: 4u)  |  |
|  +-----------------------------+--------------------+  |
+--------------------------------------------------------+
```

### 4.1 Classical Margin Scale
In traditional Renaissance book design (Van de Graaf Canon), page margins follow the harmonic proportion:

$$\text{Inner (Gutter)} : \text{Top (Head)} : \text{Outer (Fore-Edge)} : \text{Bottom (Tail)} = 1.5 : 2.0 : 3.0 : 4.0$$

### 4.2 Standard Fiction Trim Sizes
- **Trade Paperback**: $5.5\text{ in} \times 8.5\text{ in}$ ($140\text{ mm} \times 216\text{ mm}$).
- **Standard US Trade**: $6.0\text{ in} \times 9.0\text{ in}$ ($152\text{ mm} \times 229\text{ mm}$).
- **Mass Market / Pocket**: $5.0\text{ in} \times 8.0\text{ in}$ ($127\text{ mm} \times 203\text{ mm}$).
- **Royal Hardcover (UK)**: $6.14\text{ in} \times 9.21\text{ in}$ ($156\text{ mm} \times 234\text{ mm}$).

---

## 5. Typst Typesetting Template for Fiction Novels

```typst
#set page(
  paper: "us-trade", // 6in x 9in
  margin: (inside: 0.85in, outside: 0.70in, top: 0.75in, bottom: 0.85in),
  header: locate(loc => {
    let page_num = counter(page).at(loc).first()
    if page_num > 1 {
      if calc.even(page_num) {
        align(left)[#text(size: 9pt, font: "Linux Libertine")[#smallcaps("Valerius M. Vance")]]
      } else {
        align(right)[#text(size: 9pt, font: "Linux Libertine")[#smallcaps("The Sun-Cleaver")]]
      }
    }
  }),
  footer: locate(loc => {
    let page_num = counter(page).at(loc).first()
    if page_num > 1 {
      align(center)[#text(size: 10pt)[#page_num]]
    }
  })
)

#set text(
  font: "EB Garamond",
  size: 11pt,
  lang: "en",
  hyphenate: true
)

#set par(
  leading: 0.65em,       // 15pt line height
  first-line-indent: 1.5em,
  justify: true
)

// First paragraph of chapter has 0 indent
#show heading: it => {
  v(2in)
  align(center)[
    #text(size: 18pt, weight: "regular", font: "Cormorant Garamond")[#it.body]
  ]
  v(1in)
}
```

---

## 6. Word Processor & DOCX Typography Presets

| Preset Name | Typeface | Size | Line Spacing | Margins | First-Line Indent | Scene Break | Standard Use Case |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| `standard-submission` | Times New Roman | 12 pt | 2.0x (Double) | 1.0 in (All) | 0.50 in | `#` | Shunn Standard for literary agent & editor submissions. |
| `modern-manuscript` | Georgia | 11.5 pt | 1.35x | 1.0 in (All) | 0.35 in | `* * *` | High-legibility on-screen desktop reading & beta review. |
| `classic-trade` | EB Garamond | 12 pt | 1.50x | 1.0 in (All) | 0.40 in | `✦ ✦ ✦` | Publication-ready trade paperback aesthetic in DOCX. |

Configure active DOCX presets via CLI:
```bash
arcanum config docx-preset modern-manuscript
```

### 6.1 Automated In-Editor Micro-Typography
In Obsidian, the pre-bundled [`obsidian-smart-typography`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md#4-smart-typography) plugin automates micro-typography in real time as you type:
- `--` is instantly converted to an em-dash (`—`).
- Straight quotes (`"`, `'`) are converted to typographic curly quotes (`“ ”`, `‘ ’`).
- `...` is converted to a typographic ellipsis (`…`).
- `(c)`, `(tm)`, `(r)` are converted to copyright/trademark symbols (`©`, `™`, `®`).

For full details, see the [Master External Tools & Obsidian Plugins Guide](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md).

---

## 7. Recommended Reading, References & Media

### 7.1 Foundational Typographical Treatises & Classics
- **Bringhurst, Robert (2012)**. *The Elements of Typographic Style* (Version 4.0). Hartley & Marks Publishers. ISBN: 978-0881792126.  
  *The undisputed masterpiece on book typography, rhythm, proportion, dash disambiguation, and type anatomy.*
- **Tschichold, Jan (1991)**. *The Form of the Book: Essays on the Morality of Good Design*. Hartley & Marks. ISBN: 978-0881790344.  
  *Foundational essays on classical European page proportions, margins, and geometric construction.*
- **Hochuli, Jost (2015)**. *Detail in Typography*. Éditions B42. ISBN: 978-2917855607.  
  *The authoritative guide to micro-typography: letter-spacing, word spacing, leading, and measure.*
- **Warde, Beatrice (1955)**. *The Crystal Goblet: Sixteen Essays on Typography*. Sylvan Press.  
  *The philosophical classic arguing that typography should remain transparent to serve the story.*
- **Shunn, William (2019)**. *Proper Manuscript Format for Novels*. [shunn.net](https://www.shunn.net/format/novel/).  
  *The industry standard submission guideline for traditional publishing houses and literary agents.*

### 7.2 Video Lectures, Masterclasses & Typographic Media
- **Type Directors Club (TDC)**: *The Geometry of the Book: Classical Proportions and Modern Grid Layouts*.  
  *Visual masterclasses on book geometry, Tschichold grids, and margin harmonics.*
- **Ellen Lupton (MICA)**: *Thinking with Type: Visual Hierarchy and Saccadic Reading Rhythms*.  
  *How line length, measure, and font choices affect reader cognitive fatigue.*
- **Typst Community**: *Modern Book Design and Automated Typesetting with Typst*.  
  *Step-by-step masterclasses on building publication-ready book templates in Typst.*

### 7.3 Landmark Speculative Case Studies
- **Tolkien, J.R.R.**: *The Lord of the Rings* (Allen & Unwin Original Typesetting).  
  *Exemplar of classical British book design with custom calligraphy and runic typography.*
- **Danielewski, Mark Z.**: *House of Leaves* (2000).  
  *Extreme exploration of spatial typography and non-linear physical page geometry.*
- **Pratchett, Terry**: *The Discworld Series* (Gollancz / Corgi Typesetting).  
  *Distinctive typographic voicing using SMALL CAPS and iconic footnote layouts.*
