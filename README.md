# overall_reaction_diagram
Makes an overall reaction flux diagram when running Cantera simulations

First, run the script that runs the Cantera simulation.
It will make a `.dot` file.
Then run:

```
dot -Tpdf {dot_name}.dot -o{whatever_name_you_want}.pdf
```
