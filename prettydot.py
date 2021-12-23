import pandas as pd
import cantera as ct
import os
import re

from rmgpy.molecule import Molecule
from rmgpy.data.base import Database
# post processes dot file and creates a prettydot


# get smiles dictionary
def get_smiles_dict(species_dict_file):
    species_dict = Database().get_species(species_dict_file)

    rmg_names = species_dict.keys()
    # get the first listed smiles string for each molecule
    smile = []
    for s in species_dict:
        # treating HX separately because smiles translation drops the H
        if s == 'HX(5)':
            smile.append('H[Pt]')
            continue
        smile.append(species_dict[s].molecule[0])
        if len(species_dict[s].molecule) is not 1:
            print('There are %d dupllicate smiles for %s:' %
                (len(species_dict[s].molecule), s))
            for a in range(len(species_dict[s].molecule)):
                print('%s' % (species_dict[s].molecule[a]))

    # translate the molecules from above into just smiles strings
    smiles = []
    for s in smile:
        try:
            smiles.append(s.to_smiles())
        except AttributeError:
            print("Cannot convert {} to SMILES, translating manually".format(s))
            smiles.append(s)

    names = dict(zip(rmg_names, smiles))

    return names

def save_pictures(species_path="", overwrite=False):
    """
    Save a folder full of molecule pictures, needed for the pretty dot files.

    Saves them in the results directory, in a subfolder "species_pictures".
    Unless you set overwrite=True, it'll leave alone files that are
    already there.
    """
    dictionary_filename = "./species_dictionary.txt"


    smile_species_dict = get_smiles_dict(dictionary_filename)

    specs = Database().get_species(dictionary_filename, resonance=False)
    images_dir = os.path.join(species_path)
    os.makedirs(images_dir, exist_ok=True)

    for name, species in specs.items():
        spec_name = smile_species_dict[name]
        filepath = os.path.join(images_dir, spec_name + ".svg")
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

    rePicture = re.compile("(?P<smiles>.+?)\.svg")
    reLabel = re.compile("(?P<smiles>.+?)$")

    species_pictures = dict()
    for picturefile in os.listdir(pictures_directory):
        match = rePicture.match(picturefile)
        if match:
            species_pictures[match.group("smiles")] = picturefile
        else:
            pass

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
            # print(label)
            if idmatch:
                idnumber = idmatch.group("smiles")
                # print(idnumber)
                # print(species_pictures[idnumber])
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
    # os.system(
    #     f'dot {prettypath} -Tpdf -o{prettypath.replace(".dot", "", 1) + ".pdf"} -Gdpi=300')
    
    return prettypath

save_pictures("./species_pictures")
prettydot("./species_pictures", "./overall_rxn_diagram.dot")
