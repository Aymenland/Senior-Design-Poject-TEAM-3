import requests
from itertools import combinations
from datetime import datetime
import os
import pathlib


api_key = "4bFpW4dGgCprnAN0q"


def download_cif(groups, path="./cifs" + datetime.now().strftime('%Y-%m-%d %H-%M') + "/"):
    combined = []
    mydir = os.path.join(os.getcwd(), path[2: -1])
    os.makedirs(mydir)
    for group in groups:
        combined += group

    for subset in combinations(combined, len(groups)):
        # Checking wether the subset includes only one element from each group
        explored = []
        good = True
        for element in subset:
            for i, group in enumerate(groups):
                if element in group and i not in explored:
                    explored.append(i)
                    break
                elif element in group and i in explored:
                    good = False
                    break

            if not good:
                break
        if not good:
            continue

        # By here, the subset contains only one element from each group
        text = ""
        for i, element in enumerate(subset):
            text += ("-" + element) if i != 0 else element

        response = requests.get("https://www.materialsproject.org/rest/v2/materials/" + text + "/vasp?API_KEY=" +
                                api_key)
        data = response.json()["response"]

        for elem in data:
            file = open(path + elem["material_id"] + "__" + elem["full_formula"] + ".cif", "w")
            file.write(elem["cif"])


if __name__ == "__main__":
    print("This is a module that meant to be imported and used, not ran.")

"""    group1 = ["Cu", "Ag", "Au"]
    group2 = ["As", "Sb", "Bi"]
    group3 = ["Cl", "Br", "I"]
    all_groups = [group1, group2, group3]
    
    download_cif(all_groups, "./cifs/")"""