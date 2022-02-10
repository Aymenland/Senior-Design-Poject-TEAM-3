import requests
import zipfile
import io
import os
from glob import glob
from shutil import move, rmtree
import sys
import errno
import stat

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
api_key = "4bFpW4dGgCprnAN0q"
result = []


def all_possible_materials(groups):
    global result
    data = []

    permutations(groups)
    for subset in result:
        text = ""
        for i, element in enumerate(subset):
            text += ("-" + element) if i != 0 else element

        response = requests.get("https://www.materialsproject.org/rest/v2/materials/" + text + "/vasp?API_KEY=" +
                                api_key)
        data += response.json()["response"]

    result = []
    return data


def download_metadata(material):
    # Get the material's ID
    response = requests.get("https://www.materialsproject.org/rest/v2/materials/" + material + "/vasp?API_KEY=" +
                            api_key)
    material_id = response.json()["response"][0]["material_id"]

    # Get the GGA static task ID
    response = requests.get("https://materialsproject.org/materials/" + material_id + "/tasks")
    tasks = response.json()

    task_id = ""
    for task in tasks:
        if task['task_type'] == "GGA Static" and "blessed" in task:
            task_id = task["task_id"]
            break

    if not task_id:
        return 1

    # Get the raw data from nomad
    response = requests.get("https://nomad-lab.eu/prod/rae/api/v1/entries/raw/download?external_id=" + task_id
                            , stream=True)

    # Convert the data into ZIP and extract it
    z = zipfile.ZipFile(io.BytesIO(response.content))
    z.extractall(path=material + "/")

    path = glob(material + "/*/*/*/*/", recursive=True)[0]
    last_folder = path.split("\\")[-2]
    move(src=path, dst=sys.path[0])
    rmtree(material, ignore_errors=False, onerror=handle_remove_readonly)
    os.rename(src=last_folder, dst=material)


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

    download_metadata("CCl4")

    # Get the auth key
    """response = requests.post("https://nomad-lab.eu/prod/rae/api/v1/auth/token",
                             data={"username": "Aymenland", "password": ""}).json()
    print(response)"""
