// ==============================================================================
// Ars Arcanum Literary Trade Publication Preset (Typst)
// Tailored for literary fiction, psychological drama, and refined trade paperbacks.
// ==============================================================================

#let literary-trade-layout(
  title: "Literary Title",
  subtitle: "",
  author: "Author Name",
  dedication: "",
  epigraph: "",
  epigraph-author: "",
  year: "2026",
  isbn: "978-0-000000-00-0",
  publisher: "Ars Arcanum Press",
  paper-size: "trade", // "trade" (5.5x8.5in) or "us-trade" (6x9in)
  body-font: "Linux Libertine",
  font-size: 10.5pt,
  line-spacing: 0.70em,
  body
) = {

  let (width, height) = if paper-size == "trade" {
    (5.5in, 8.5in)
  } else {
    (6in, 9in)
  }

  set document(title: title, author: author)

  set text(
    font: (body-font, "Libertinus Serif", "EB Garamond", "DejaVu Serif"),
    size: font-size,
    lang: "en"
  )

  set par(
    justify: true,
    first-line-indent: 1.4em,
    leading: line-spacing
  )

  set page(
    width: width,
    height: height,
    margin: (
      inside: 0.85in,
      outside: 0.70in,
      top: 0.80in,
      bottom: 0.80in
    ),
    header: none,
    footer: none
  )

  // --- Title Page ---
  align(center + horizon)[
    #v(3cm)
    #text(size: 20pt, style: "italic")[#title]
    #if subtitle != "" [
      #v(0.5cm)
      #text(size: 11pt, fill: luma(80))[#subtitle]
    ]
    #v(2cm)
    #text(size: 12pt, tracking: 0.05em)[#author]
    #v(4cm)
    #text(size: 8.5pt, fill: luma(100))[#publisher]
  ]
  pagebreak()

  // --- Copyright Page ---
  align(bottom + left)[
    #set text(size: 8pt, fill: luma(70))
    #set par(first-line-indent: 0pt, leading: 0.45em)
    Published by #publisher \
    Copyright © #year by #author \
    All rights reserved. \
    ISBN: #isbn
  ]
  pagebreak()

  // --- Header & Running Footer ---
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
      align(center)[#text(size: 8.5pt, fill: luma(70))[#loc.page()]]
    })
  )

  show heading.where(level: 1): it => {
    pagebreak()
    align(center)[
      #v(3cm)
      #text(size: 15pt, weight: "regular", style: "italic")[#it.body]
      #v(1.5cm)
    ]
  }

  body
}
