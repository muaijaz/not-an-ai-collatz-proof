# Paper Build

This directory contains the v0 arXiv-shaped paper draft generated from the
repository notes and JSON artifact catalog.

## Requirements

- `uv` for the default figure-script runner, or Python 3 with `matplotlib` if
  you override `PYTHON`
- A LaTeX installation with `pdflatex`, `bibtex`, and the packages used by
  `main.tex`

## Build

```bash
make
```

The default target rebuilds all figures from the JSON artifacts and then builds
`main.pdf`.

## arXiv Bundle

```bash
make arxiv
```

This produces `arxiv/collatz-renewal-paper.tar.gz` with the TeX sources,
BibTeX file, figure scripts, and regenerated PDF figures.

## Clean

```bash
make clean
```
