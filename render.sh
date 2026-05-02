read -rp "Nom de l'auteur : " AUTHOR
pandoc repport.md -o output.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=2.5cm \
  -V mainfont="Latin Modern Roman" \
  -V fontsize=11pt \
  -V 'header-includes=\usepackage{newunicodechar}\newunicodechar{⟨}{\ensuremath{\langle}}\newunicodechar{⟩}{\ensuremath{\rangle}}\newunicodechar{≈}{\ensuremath{\approx}}\newunicodechar{∩}{\ensuremath{\cap}}\newunicodechar{∪}{\ensuremath{\cup}}\newunicodechar{∈}{\ensuremath{\in}}\newunicodechar{≫}{\ensuremath{\gg}}\usepackage{float}\floatplacement{figure}{H}' \
  -V 'include-before=\pagenumbering{arabic}\setcounter{page}{1}\thispagestyle{empty}\begin{center}\vspace*{2cm}{\scshape\Large Télécom SudParis\par}\vspace{0.5cm}{\large NET 4103 — Réseaux complexes et validation\par}\vspace{4cm}{\huge\bfseries Analyse du dataset Facebook100\par}\vspace{1cm}{\Large\itshape Projet de fin de module\par}\vspace{4cm}{\Large\textbf{'"$AUTHOR"'}\par}\vspace{0.5cm}{\large \today\par}\vspace{2cm}{\small Code source : \url{https://github.com/zroumane/net4103_projet}\par}\end{center}\newpage\tableofcontents\newpage' \
  -V 'toc-title=Table des matières' \
  --highlight-style=tango
