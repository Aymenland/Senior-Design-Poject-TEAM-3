from pymatgen.io.vasp import Poscar
from pymatgen.io.cif import CifWriter


def convert(vasp_file, output_file):
    try:
        poscar = Poscar.from_file(vasp_file)
        w = CifWriter(poscar.structure)
        w.write_file(output_file)
    except Exception:
        print("Invalid VASP structure.")


if __name__ == "__main__":
    print("This is a module that meant to be imported and used, not ran.")
