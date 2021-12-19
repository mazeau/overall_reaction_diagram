import pandas as pd
import cantera as ct
import os
import re

from rmgpy.molecule import Molecule
from rmgpy.data.base import Database
# post processes dot file and creates a prettydot

def save_pictures(species_path="", overwrite=False):
    """
    Save a folder full of molecule pictures, needed for the pretty dot files.

    Saves them in the results directory, in a subfolder "species_pictures".
    Unless you set overwrite=True, it'll leave alone files that are
    already there.
    """
    dictionary_filename = "./species_dictionary.txt"
    specs = Database().get_species(dictionary_filename, resonance=False)
    images_dir = os.path.join(species_path)
    os.makedirs(images_dir, exist_ok=True)

    for name, species in specs.items():
        filepath = os.path.join(images_dir, name + ".svg")
        if not overwrite and os.path.exists(filepath):
            continue
        species.molecule[0].draw(filepath)

def prettydot(species_path="", dotfilepath="", strip_line_labels=False):
    """
    Make a prettier version of the dot file (flux diagram)

    Assumes the species pictures are stored in a directory
    called 'species_pictures' alongside the dot file.
    """
    pictures_directory = f'{species_path}/'

    if strip_line_labels:
        print("stripping edge (line) labels")

    reSize = re.compile('size="5,6"\;page="5,6"')

    # the "shape" arguement is different from the cantera output, 
    # if you use that you can just remove "shape=box \" or put a regex 
    # wildcard there I guess 

    reNode = re.compile(
        '(?P<node>s\d+)\ \[\ fontname="Helvetica",\ shape=box,\ label="(?P<label>[^"]*)"\]\;'
    )

    rePicture = re.compile("(?P<smiles>.+?)\((?P<id>\d+)\)\.svg")
    reLabel = re.compile("(?P<name>.+?)\((?P<id>\d+)\)$")

    species_pictures = dict()
    for picturefile in os.listdir(pictures_directory):
        match = rePicture.match(picturefile)
        if match:
            species_pictures[match.group("id")] = picturefile
        else:
            pass
            # print(picturefile, "didn't look like a picture")

    filepath = dotfilepath

    if not open(filepath).readline().startswith("digraph"):
        raise ValueError("{0} - not a digraph".format(filepath))

    infile = open(filepath)
    prettypath = filepath.replace(".dot", "", 1) + "-pretty.dot"
    outfile = open(prettypath, "w")

    for line in infile:
        (line, changed_size) = reSize.subn(
            'size="12,12";page="12,12"', line)
        match = reNode.search(line)
        if match:
            label = match.group("label")
            idmatch = reLabel.match(label)
            if idmatch:
                idnumber = idmatch.group("id")
                if idnumber in species_pictures:
                    line = (
                        f'%s [ image="{pictures_directory}%s" label="" width="1.0" height="1.0" imagescale=true fixedsize=false color="none" ];\n'
                        % (match.group("node"), species_pictures[idnumber])
                    )

        # rankdir="LR" to make graph go left>right instead of top>bottom
        if strip_line_labels:
            line = re.sub('label\s*=\s*"\s*[\d.]+"', 'label=""', line)

        # change colours
        line = re.sub('color="0.7,\ (.*?),\ 0.9"',
                        r'color="1.0, \1, 0.7*\1"', line)

        outfile.write(line)

    outfile.close()
    infile.close()
    print(f"Graph saved to: {prettypath}")

    # if this gives you an error, just put the usual dot command in your terminal: 
    # dot overall_rxn_diagram-pretty.dot -Tpdf -o overall_rxn_diagram-pretty.pdf -Gdpi=300
    # I somehow have dot partially working for me, so the script runs through without an error
    os.system(
        f'dot {prettypath} -Tpdf -o{prettypath.replace(".dot", "", 1) + ".pdf"} -Gdpi=300')
    return prettypath

save_pictures("./species_pictures")
prettydot("./species_pictures", "./overall_rxn_diagram.dot")
