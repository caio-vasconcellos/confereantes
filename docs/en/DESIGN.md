# Design notes

[English](DESIGN.md) · [Português](../../DESIGN.md)

The interface is a comparison desk with two documents: the original offer (A) and the payment request (B). The [≠] mark refers to comparing them, not to a verdict about the payment.

An orange side panel tracks added evidence. The reading surface holds the documents and results; optional payment details sit in an expandable section.

## Choices

- Signal orange, desk gray and black. Warning colors are also accompanied by text.
- Condensed headings and monospaced document labels.
- Lined text fields, A/B document labels and numbered findings.
- No external fonts or downloaded interface artwork.
- Keyboard navigation, a skip link and reduced-motion support.
- A single-column layout on smaller screens.
- A language switch outside the form; English labels use the same layout.

Styles are in `src/confereantes/static/workbench.css`.

## References

[Hoverstat.es](https://www.hoverstat.es/archive/?tagged=experimental), [Treize Grammes](https://www.13g.fr/) and [Are.na](https://www.are.na/) informed the visual exploration. No proprietary assets or code from those sites are included.

The README organization was reviewed against [Cyber Incidents Explorer](https://github.com/gabriel-zomignani/cyber-incidents-explorer). ConfereAntes keeps its own stack and local-only workflow; it does not use that project's cloud-model setup.
