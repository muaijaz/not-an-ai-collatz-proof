PYTHON ?= uv run --with matplotlib python
PDFLATEX ?= pdflatex
BIBTEX ?= bibtex

FIGURES = figures/drift_residual_n0.pdf \
	figures/foster_residue_obstruction.pdf \
	figures/m_step_foster_transition.pdf

.PHONY: paper figures clean arxiv

paper: main.pdf

main.pdf: main.tex references.bib $(wildcard sections/*.tex) $(FIGURES)
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error main.tex
	$(BIBTEX) main
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error main.tex
	$(PDFLATEX) -interaction=nonstopmode -halt-on-error main.tex

figures: $(FIGURES)

figures/drift_residual_n0.pdf: figures/scripts/drift_residual_n0.py ../docs/reports/renewal_drift_phase_decomposed_n0_stability.json
	$(PYTHON) figures/scripts/drift_residual_n0.py

figures/foster_residue_obstruction.pdf: figures/scripts/foster_residue_obstruction.py ../docs/reports/phase_lyapunov_foster_drift.json
	$(PYTHON) figures/scripts/foster_residue_obstruction.py

figures/m_step_foster_transition.pdf: figures/scripts/m_step_foster_transition.py ../docs/reports/m_step_foster_drift.json
	$(PYTHON) figures/scripts/m_step_foster_transition.py

clean:
	rm -f main.aux main.bbl main.bcf main.blg main.log main.out main.pdf main.run.xml main.toc
	rm -f $(FIGURES)
	rm -rf arxiv

arxiv: main.pdf
	rm -rf arxiv
	mkdir -p arxiv/source/sections arxiv/source/figures/scripts
	cp main.tex references.bib README.md Makefile arxiv/source/
	cp sections/*.tex arxiv/source/sections/
	cp figures/*.pdf arxiv/source/figures/
	cp figures/scripts/*.py arxiv/source/figures/scripts/
	cd arxiv/source && tar -czf ../collatz-renewal-paper.tar.gz .
