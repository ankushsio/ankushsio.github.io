// ============================================================================
// One-page resume template — ATS-first.
//
// Reads `data.json`, which scripts/render_resume.py generates from
// content/career.json plus a variant file. Do not hand-edit data.json.
//
// ATS rules deliberately encoded here, because these are what actually break
// parsers (the toolchain never does):
//   * one column, no tables, no text boxes, no images, no icons
//   * contact details in the document BODY, never in a page header/footer
//   * standard section headings: Summary / Experience / Skills / Education
//   * a widely available font with clean text extraction
//   * URLs written as readable text, not hidden behind link labels
//   * consistent "Mon YYYY" dates
// ============================================================================

#let data = json("data.json")

#set page(
  paper: "us-letter",
  // No header/footer: anything there is frequently dropped by resume parsers.
  margin: (x: 0.5in, top: 0.5in, bottom: 0.5in),   // 0.5in is the floor; never go below
)

#set text(
  font: ("Calibri", "Carlito", "Liberation Sans", "Arial"),
  size: 10.2pt,
  lang: "en",
)
#set par(justify: false, leading: 0.54em, spacing: 0.58em)
#show link: it => it  // keep link text visible and extractable

// Section heading: plain uppercase word plus a rule. No graphics.
#let section(title) = {
  v(0.42em)
  block(
    width: 100%,
    stroke: (bottom: 0.6pt + rgb("#333333")),
    inset: (bottom: 2.2pt),
    text(size: 10.5pt, weight: "bold", tracking: 0.06em, upper(title)),
  )
  v(0.30em)
}

// --- header -----------------------------------------------------------------

#block[
  #text(size: 19pt, weight: "bold")[#data.name]
  #linebreak()
  #v(0.10em)
  #text(size: 10.6pt, fill: rgb("#333333"))[#data.title]
]
// Must stay on ONE line: a method chain broken across newlines ends the code
// expression, and Typst then prints the remainder as literal text.
#let contact-line = data.contact.map(c => if c.url == "" { c.label } else { link(c.url, c.label) }).join("  |  ")

#v(0.18em)
#text(size: 9.6pt)[#contact-line]
#v(0.30em)

// --- summary ----------------------------------------------------------------

#section("Summary")
#data.summary

// --- experience -------------------------------------------------------------

#section("Experience")

#for job in data.experience [
  #block(width: 100%)[
    #grid(
      columns: (1fr, auto),
      align: (left, right),
      text(weight: "bold", size: 11pt)[#job.company],
      text(size: 9.8pt)[#job.dates],
    )
    #v(-0.30em)
    // One row per title. Where a promotion happened this shows both, dated, so the
    // progression is visible rather than just the latest label.
    //
    // The negative space goes BEFORE each row after the first. Applied after every
    // row it also lands between them, and -0.55em against 0.58em of paragraph
    // spacing left ~0.03em of leading -- with one role that is invisible, with the
    // two rows of a promotion they collide and the date dashes cut through the line
    // above. Keep this tied to the gap it is closing.
    #for (i, r) in job.roles.enumerate() [
      #if i > 0 [ #v(-0.42em) ]
      #grid(
        columns: (1fr, auto),
        align: (left, right),
        text(size: 10.2pt, style: "italic")[#r.title],
        text(size: 9.4pt, fill: rgb("#444444"))[#r.dates],
      )
    ]
    // No #linebreak() here: the note already starts a new paragraph, so a break on
    // top of it opened the largest gap on the page for no reason.
    #if job.note != "" [
      #v(0.24em)
      #text(size: 9.5pt, fill: rgb("#444444"))[#job.note]
    ]
  ]
  #v(0.22em)

  #for group in job.groups [
    #if group.label != "" [
      #text(weight: "bold", size: 10pt)[#group.label]
      #if group.dates != "" [
        #text(size: 9.4pt, fill: rgb("#444444"))[ (#group.dates)]
      ]
      #v(0.06em)
    ]
    #list(
      indent: 0.10in,
      body-indent: 0.13in,
      spacing: 0.34em,
      marker: [•],
      ..group.bullets,
    )
    #v(0.24em)
  ]
]

// --- skills -----------------------------------------------------------------

#section("Skills")
#for row in data.skills [
  #text(weight: "bold")[#row.label:] #row.items
  #linebreak()
]

// --- education --------------------------------------------------------------

#if data.education.len() > 0 [
  #section("Education")
  #for e in data.education [
    #grid(
      columns: (1fr, auto),
      align: (left, right),
      [#text(weight: "bold")[#e.institution] — #e.degree],
      text(size: 9.8pt)[#e.dates],
    )
  ]
]

// --- achievements -----------------------------------------------------------

// One joined paragraph, not a row per item: three awards as three lines would spend
// more of the page on labels than on the awards.
#if data.achievements.len() > 0 [
  #section("Achievements")
  #data.achievements.join("; ")
]
