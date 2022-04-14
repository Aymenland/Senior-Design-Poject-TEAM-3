import requests
import zipfile
import os
from glob import glob
from shutil import move, rmtree, copy, copyfileobj
import sys
import errno
import stat
import gzip

api_key_nomad = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmb1hmZnM5QlFQWHduLU54Yk5PYlExOFhnZnlKU1FNRkl6ZFVnWjhr" \
                "ZzdVIn0.eyJqdGkiOiI4NzRkNDU4My0xODRjLTRmMGQtODdiZi1hYmJjZTVlOTA5YmUiLCJleHAiOjE2NDM2NTE3NjEsIm5iZiI6MCwi" \
                "aWF0IjoxNjQzNTY1MzYxLCJpc3MiOiJodHRwczovL25vbWFkLWxhYi5ldS9mYWlyZGkva2V5Y2xvYWsvYXV0aC9yZWFsbXMvZmFpcmRp" \
                "X25vbWFkX3Byb2QiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiNmMxZGFiZWMtYmE5Ny00Zjk2LTllMzYtMGVkNmYwMGVlYjQ2IiwidHlw" \
                "IjoiQmVhcmVyIiwiYXpwIjoibm9tYWRfcHVibGljIiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiMmYyNjVmNjktOTkzNC00" \
                "OTM0LWIzN2MtNDdkNDYyYjhiYjViIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xl" \
                "cyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xl" \
                "cyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxl" \
                "IGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJBeW1lbiBTYWlkaSIsInByZWZlcnJlZF91c2VybmFtZSI6ImF5bWVu" \
                "bGFuZCIsImdpdmVuX25hbWUiOiJBeW1lbiIsImZhbWlseV9uYW1lIjoiU2FpZGkiLCJlbWFpbCI6ImF5bWVuLnN1aWRpQGdtYWlsLmNv" \
                "bSJ9.S8SB7zVm8M-KbwFeZ1T7nuHV7gXzbVHlxcaxfux_rQhfDIMgADW5bkv5uav7B2Ef4fCelU_4vSfEQZoIegQfaO0o6z8TdTrptTu" \
                "tfYBvsYygSQsjyzFe4CSxxt-8lJgpf6cgRSEPPn_6lduNipKzVmw04nsQM6UGkhkVztU2FVOmhjV3CrFzv_tjYcIwP54ARudu9PnvRPM" \
                "MrhWtRvw4zYlHhtszsmA5pUzPqdZsMTLlIDm75ZZX528-TLd-Uh6TOKCOdohY8gahGYHTKqRw-FNIJPiFBUDnfzzVgZBNwZloFQyW8vk" \
                "0zBITi4kcmb1RnCGsXgi1N2qQEWPmztMvBg"
api_key = "AQcSK0zedptvIX5R"
result = []


def convert_number(num, modif):
    if len(str(float(num) * modif)) <= 8:
        num = str(float(num) * modif).ljust(8, "0")
    else:
        num = str(float(num) * modif)[:8]

    return num


def all_possible_materials(groups):
    global result
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

    result = []
    return data


def download_metadata(material_id, material):
    # Get the GGA static task ID
    response = requests.get("https://legacy.materialsproject.org/materials/" + material_id + "/tasks")
    tasks = response.json()

    task_id = ""
    for task in tasks:
        if task['task_type'] == "GGA Static" and "blessed" in task:
            task_id = task["task_id"]
            break

    if not task_id:
        return 1

    # Get the raw data from nomad
    elem_headers = requests.head("https://nomad-lab.eu/prod/rae/api/v1/entries/raw/download?external_id=" + task_id
                                 , stream=True)
    block_size = int(elem_headers.headers.get('content-length'))

    response = requests.get("https://nomad-lab.eu/prod/rae/api/v1/entries/raw/download?external_id=" + task_id
                            , stream=True)

    # Convert the data into ZIP and extract it
    download_size = 0
    old_download_size = 0
    flag = False

    with open(material + ".zip", "wb") as f:
        for data in response.iter_content(block_size):
            if not len(data):
                break

            download_size += block_size
            f.write(data)

            if download_size // (10 ** 6) != old_download_size // (10 ** 6):
                if flag:
                    sys.stdout.flush()
                sys.stdout.write("\rSize of data downloaded: " + str(download_size // (10 ** 6)) + "MB")
                flag = True

            old_download_size = download_size

    with zipfile.ZipFile(material + ".zip", 'r') as zip_ref:
        zip_ref.extractall(path=material + "/")
    print()

    os.remove(material + ".zip")

    path = glob(material + "/*/*/*/*/", recursive=True)[0]
    last_folder = path[path.find("launcher"): -1]
    move(src=path, dst=sys.path[0])
    rmtree(material, ignore_errors=False, onerror=handle_remove_readonly)
    os.rename(src=last_folder, dst="OriginalData")

    # SubFolder 2 Contains the KPoint File and Car Files
    os.makedirs("InputFiles")

    files_to_move = ['KPOINTS.gz', 'INCAR.gz', 'POSCAR.gz']
    source_folder = 'OriginalData/'
    destination_folder = 'InputFiles/'

    for file in files_to_move:
        # Construct full file path
        source = source_folder + file
        destination = destination_folder
        # Move file
        try:
            move(source, destination)
        except FileNotFoundError:
            pass

    os.makedirs(material)

    # Move both subfolders to the main material folder
    folders_to_move = ["OriginalData", "InputFiles"]
    destination_folder = material

    for file in folders_to_move:
        move(file, destination_folder)


def supercell(nx, ny, nz, material):
    folder = material + "/Supercell_" + str(nx) + "_" + str(ny) + "_" + str(nz)
    os.makedirs(folder)

    # POTCAR & INCAR

    copy(material + "/InputFiles/POTCAR", folder)
    copy(material + "/InputFiles/INCAR.gz", folder)

    # KPOINTS

    with gzip.open(material + "/InputFiles/KPOINTS.gz", 'rb') as f_in:
        with open(folder + "/KPOINTS", 'wb') as f_out:
            copyfileobj(f_in, f_out)

    with open(folder + "/KPOINTS", "r") as file:
        kpoints = file.read()

    with open(folder + "/KPOINTS", "w") as file:
        line = kpoints.split("\n")[-2]
        nums = [int(n) for n in line.split(" ")]
        nums = [str(int(round(nums[0] / nx, 0))), str(int(round(nums[1] / ny, 0))), str(int(round(nums[2] / nz, 0)))]
        kpoints_new = kpoints[:kpoints.find(line)] + " ".join(nums) + "\n"
        file.write(kpoints_new)

    # POSCAR

    with gzip.open(material + "/InputFiles/POSCAR.gz", 'rb') as f_in:
        with open(folder + "/POSCAR", 'wb') as f_out:
            copyfileobj(f_in, f_out)

    with open(folder + "/POSCAR", "r") as file:
        poscar = file.read().split("\n")

    with open(folder + "/POSCAR", "w") as file:
        poscar_new = poscar[:2]
        matrix = poscar[2: 5]
        for i, line in enumerate(matrix):
            modif = 0
            if i == 0:
                modif = nx
            elif i == 1:
                modif = ny
            else:
                modif = nz
            numbers = line.split(" ")
            for j, number in enumerate(numbers):
                numbers[j] = convert_number(numbers[j], modif)

            line = " ".join(numbers)
            matrix[i] = line

        poscar_new += matrix
        poscar_new.append(poscar[5])
        poscar_new.append(" ".join([str(int(elem) * nx * ny * nz) for elem in poscar[6].split(" ")]))
        poscar_new.append(poscar[7])

        matrix = {}
        for line in poscar[8:]:
            if not line.strip():
                continue
            line = line.split(" ")

            atom = line[-1]
            if atom in matrix:
                matrix[atom].append([float(elem) for elem in line[:-1]])
            else:
                matrix[atom] = [[float(elem) for elem in line[:-1]]]

        for atom, value in matrix.items():
            for i in range(1, nx + 1):
                for j in range(1, ny + 1):
                    for k in range(1, nz + 1):
                        for lst in value:
                            temp = [(lst[0] + i - 1) / nx, (lst[1] + j - 1) / ny, (lst[2] + k - 1) / nz]
                            temp = [convert_number(str(num), 1) for num in temp]
                            poscar_new.append(" ".join(temp) + " " + atom)

        poscar_new = "\n".join(poscar_new) + "\n"

        file.write(poscar_new)


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


def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise


if __name__ == "__main__":
    print("This is a module that meant to be imported and used, not ran.")

    supercell(2, 2, 1, "C2Cl6")

    # Get the auth key
    """response = requests.post("https://nomad-lab.eu/prod/rae/api/v1/auth/token",
                             data={"username": "Aymenland", "password": ""}).json()
    print(response)"""
