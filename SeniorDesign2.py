import requests
from datetime import datetime
import os


api_key = "4bFpW4dGgCprnAN0q"
result = []


def download_cif(groups, path="./cifs" + datetime.now().strftime('%Y-%m-%d %H-%M-%S') + "/"):
    global result
    mydir = os.path.join(os.getcwd(), path[2: -1])
    os.makedirs(mydir)
    data = []

    permutations(groups)
    for subset in result:
        text = ""
        for i, element in enumerate(subset):
            text += ("-" + element) if i != 0 else element

        response = requests.get("https://www.materialsproject.org/rest/v2/materials/" + text + "/vasp",
                                headers={"x-api-key": api_key})
        if "response" not in response.json():
            return 1
        data += response.json()["response"]

    for elem in data:
        file = open(path + elem["material_id"] + "__" + elem["full_formula"] + ".cif", "w")
        file.write(elem["cif"])
        file.close()

    result = []
    return data


def permutations(groups, subset=None, c=0):
    global result
    if subset is None:
        subset = []

    if len(subset) == len(groups):
        result.append(subset)
        return

    for elem in groups[c]:
        permutations(groups, subset + [elem], c + 1)


def filter_materials(data, parameter, specification):
    data1 = []
    if specification.count(" "):
        tpl = specification.split(" ")
        try:
            tpl = tuple(float(i.strip()) for i in tpl)
        except ValueError:
            return 1
        for elem in data:
            if tpl[0] <= elem[parameter] <= tpl[1]:
                data1.append(elem)

    else:
        if parameter == "spacegroup (symbol)":
            for elem in data:
                if elem["spacegroup"]["symbol"] == specification:
                    data1.append(elem)
        else:
            for elem in data:
                if str(elem[parameter]).lower() == specification.lower():
                    data1.append(elem)

    return data1


if __name__ == "__main__":
    print("This is a module that meant to be imported and used, not ran.")

    """group1 = ["Cu", "Ag", "Au"]
    group2 = ["As", "Sb", "I"]
    group3 = ["Cl", "Br", "Bi"]"""
    group1 = ["Cu"]
    group2 = ["I"]
    group3 = ["Br"]
    all_groups = [group1, group2, group3]

    data = download_cif(all_groups)
    for line in data:
        print(line)

    data1 = filter_materials(data, "full_formula", "Cu2I1Br1")
    print("\n")
    for line in data1:
        print(line)
