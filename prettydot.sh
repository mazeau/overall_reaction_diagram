#!/bin/bash
# I had to do this to get my dot build to work. it might be fine for you
source activate rmg_env
python overall_flux_diagram.py
python prettydot.py
source deactivate
source deactivate
dot -Tpdf overall_rxn_diagram-pretty.dot -o overall_rxn_diagram-pretty.pdf -Gdpi=300