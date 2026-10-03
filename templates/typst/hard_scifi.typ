// ==============================================================================
// Ars Arcanum Hard Sci-Fi Publication Preset (Typst)
// Tailored for speculative science fiction, technical worldbuilding, and hard space opera.
// ==============================================================================

#let hard-scifi-layout(
  title: "Hard Sci-Fi Title",
  subtitle: "Orbital Mechanics & Relativistic Log",
  author: "Author Name",
  dedication: "",
  epigraph: "",
  epigraph-author: "",
  stardate: "CYCLE 248.12",
  year: "2026",
  isbn: "978-0-000000-00-0",
  publisher: "Ars Arcanum Press",
  paper-size: "us-trade", // "us-trade" (6x9in) or "demy" (5.43x8.5in)
  body-font: "Liberation Serif",
  mono-font: "Liberation Mono",
  font-size: 10pt,
  line-spacing: 0.62em,
  body
) = {

  let (width, height) = if paper-size == "demy" {
    (5.43in, 8.5in)
  } else {
    (6in, 9in)
  }

  set document(title: title, author: author)

  set text(
    font: (body-font, "Linux Libertine", "DejaVu Serif"),
    size: font-size,
    lang: "en"
  )

  set par(
    justify: true,
    first-line-indent: 1.2em,
    leading: line-spacing
  )

  set page(
    width: width,
    height: height,
    margin: (
      inside: 0.85in,
      outside: 0.70in,
      top: 0.75in,
      bottom: 0.75in
    ),
    header: none,
    footer: none
  )

  // --- Title Page ---
  align(center + horizon)[
    #text(font: mono-font, size: 8.5pt, tracking: 0.2em, fill: luma(90))[--- MISSION TELEMETRY LOG // #stardate ---]
    #v(1.5cm)
    #text(font: (body-font), size: 22pt, weight: "bold", tracking: 0.08em)[#upper(title)]
    #if subtitle != "" [
      #v(0.4cm)
      #text(font: mono-font, size: 10pt, fill: luma(80))[#subtitle]
    ]
    #v(1.8cm)
    #text(font: mono-font, size: 9pt)[#author]
    #v(3cm)
    #text(font: mono-font, size: 8pt, fill: luma(100))[SYS // #publisher]
  ]
  pagebreak()

  // --- Copyright Page ---
  align(bottom + left)[
    #set text(font: mono-font, size: 7.5pt, fill: luma(70))
    #set par(first-line-indent: 0pt, leading: 0.4em)
    DOCUMENT ID: #isbn \
    AUTHOR IDENT: #author \
    CHRONOLOGY: #year \
    IMPRINT: #publisher \
    OFFLINE SOVEREIGN GENERATION COMPLIANT.
  ]
  pagebreak()

  // --- Header & Running Footer ---
  set page(
    header: locate(loc => {
      let page-num = loc.page()
      if calc.even(page-num) {
        align(left)[#text(font: mono-font, size: 7.5pt, fill: luma(90))[#author // SEC.#page-num]]
      } else {
        align(right)[#text(font: mono-font, size: 7.5pt, fill: luma(90))[#upper(title) // #stardate]]
      }
    }),
    footer: locate(loc => {
      align(center)[#text(font: mono-font, size: 8pt, fill: luma(70))[[ #loc.page() ]]]
    })
  )

  show heading.where(level: 1): it => {
    pagebreak()
    align(left)[
      #v(1.5cm)
      #text(font: mono-font, size: 8.5pt, fill: luma(100))[--- SECTOR ENTRY // TRANSMISSION ---]
      #v(0.3cm)
      #text(font: body-font, size: 16pt, weight: "bold")[#it.body]
      #v(0.2cm)
      #line(length: 100%, stroke: 0.5pt + luma(150))
      #v(0.8cm)
    ]
  }

  body
}
