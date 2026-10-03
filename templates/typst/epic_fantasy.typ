// ==============================================================================
// Ars Arcanum Epic Fantasy Publication Preset (Typst)
// Tailored for high fantasy sagas, multi-POV epics, and 500+ page worldbuilding tomes.
// ==============================================================================

#let epic-fantasy-layout(
  title: "Epic Fantasy Title",
  subtitle: "A Chronicle of Arcane Lore",
  author: "Author Name",
  dedication: "",
  epigraph: "",
  epigraph-author: "",
  year: "2026",
  isbn: "978-0-000000-00-0",
  publisher: "Ars Arcanum Press",
  paper-size: "royal", // "royal" (6.14x9.21in) or "us-trade" (6x9in)
  body-font: "EB Garamond",
  heading-font: "Cinzel",
  font-size: 10pt,
  line-spacing: 0.68em,
  body
) = {

  let (width, height) = if paper-size == "royal" {
    (6.14in, 9.21in)
  } else {
    (6in, 9in)
  }

  set document(title: title, author: author)

  set text(
    font: (body-font, "Libertinus Serif", "Linux Libertine", "DejaVu Serif"),
    size: font-size,
    lang: "en"
  )

  set par(
    justify: true,
    first-line-indent: 1.5em,
    leading: line-spacing
  )

  // Generous gutter binding for thick high-fantasy tomes
  set page(
    width: width,
    height: height,
    margin: (
      inside: 0.95in,
      outside: 0.70in,
      top: 0.80in,
      bottom: 0.80in
    ),
    header: none,
    footer: none
  )

  // --- Title Page ---
  align(center + horizon)[
    #v(2cm)
    #text(font: (heading-font, body-font), size: 24pt, weight: "bold", tracking: 0.15em)[#upper(title)]
    #if subtitle != "" [
      #v(0.6cm)
      #text(font: (heading-font, body-font), size: 13pt, style: "italic")[#subtitle]
    ]
    #v(1.5cm)
    #text(size: 10pt, tracking: 0.2em)[✦ ✦ ✦]
    #v(1.5cm)
    #text(font: (heading-font, body-font), size: 14pt)[#author]
    #v(3cm)
    #text(size: 9pt, fill: luma(80))[#publisher]
  ]
  pagebreak()

  // --- Copyright Page ---
  align(bottom + left)[
    #set text(size: 8pt, fill: luma(60))
    #set par(first-line-indent: 0pt, leading: 0.45em)
    #title \
    Copyright © #year by #author. All rights reserved. \
    Published by #publisher. \
    ISBN: #isbn \
    Typeset via Ars Arcanum Sovereign OS.
  ]
  pagebreak()

  // --- Dedication / Epigraph ---
  if epigraph != "" [
    align(center + horizon)[
      #block(width: 75%)[
        #set text(style: "italic", size: 9.5pt)
        #epigraph
        #if epigraph-author != "" [
          #v(0.5em)
          #align(right)[--- #epigraph-author]
        ]
      ]
    ]
    pagebreak()
  ]

  // --- Main Body with Header & Running Footer ---
  set page(
    header: locate(loc => {
      let page-num = loc.page()
      if calc.even(page-num) {
        align(left)[#text(size: 8pt, style: "italic", fill: luma(80))[#author]]
      } else {
        align(right)[#text(size: 8pt, style: "italic", fill: luma(80))[#title]]
      }
    }),
    footer: locate(loc => {
      align(center)[#text(size: 8.5pt, fill: luma(60))[#loc.page()]]
    })
  )

  show heading.where(level: 1): it => {
    pagebreak()
    align(center)[
      #v(2.5cm)
      #text(size: 10pt, tracking: 0.25em, fill: luma(100))[✦ ✦ ✦]
      #v(0.5cm)
      #text(font: (heading-font, body-font), size: 17pt, weight: "bold", tracking: 0.1em)[#upper(it.body)]
      #v(1.2cm)
    ]
  }

  body
}
