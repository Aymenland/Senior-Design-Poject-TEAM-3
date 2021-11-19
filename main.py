import sys
from colorama import init
from termcolor import cprint, colored
from pyfiglet import figlet_format
from os import system
import subprocess
import SeniorDesign2
import SeniorDesign3
from datetime import datetime


def print_menu():
    init(strip=not sys.stdout.isatty())
    cprint(figlet_format('AIO Physics Tool'),
           'green', attrs=['bold'])
    print(colored('Tool Created By: Team  3 \n\n', 'cyan'))


def print_options():
    user_input = True

    while user_input:
        print(colored('  [1] - .Cif To .Vasp Converter', 'yellow'))
        print(colored('  [2] - Download .Cif files from MaterialsProject.Org', 'yellow'))
        print(colored('  [3] - .Vasp To .Cif Converter', 'yellow'))
        print(colored('  [4] - Exit Tool', 'yellow'))
        print(colored("  Selection: ", 'cyan'), end='')

        user_input = input()

        if user_input == "1":

            user_input = input('\n  Enter the filename (With the .Cif extension) to convert to .Vasp: ')
            print(colored("\n-------------------------------", 'cyan'))
            list_files = subprocess.run(["python", "SeniorDesign1.py", user_input.strip()])

            if not list_files.returncode:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion Failed. The exit code was: %d" % list_files.returncode, 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "2":

            number_groups = int(input('\n  Enter the amount of (Groups of elements): '))
            groups = []
            for i in range(number_groups):
                groups.append([elem.strip().title() for elem in
                               input("  Enter the the elements of group " + str(i) +
                                     ", separated by a comma (Example: Au,O,Br) : ").split(",")])

            print(colored("\n-------------------------------", 'cyan'))
            date = datetime.now().strftime('%Y-%m-%d_%H-%M')
            text = "Successfully Downloaded .Cif Files, Folder name: /cifs" + date
            print(colored("Downloading...", 'green'))
            data = SeniorDesign2.download_cif(groups, "./cifs" + date + "/")
            print(colored(text, 'green'))

            answer = input('\n  Would you like to convert some of the .Cif files downloaded to .Vasp format (Y/N)? ')
            options = ["formation_energy_per_atom", "pretty_formula", "e_above_hull", "spacegroup (symbol)",
                       "band_gap", "nsites", "density", "volume"]
            parameters = ["Formation Energy (eV)", "Formula", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Band Gab (eV)", "Nsites", "Density", "Volume"]
            parameters = {parameter: option for parameter, option in zip(parameters, options)}

            if answer.strip().lower() == "y":
                print("\n  These are the parameters you can filter materials by:")
                for i, parameter in enumerate(list(parameters.keys())):
                    print("\n\t", str(i) + ".", parameter)

            while answer.strip().lower() == "y":
                option = int(input('\n\n  Choose one of the parameters above (enter a number): ').strip().lower())
                specification = input("\n\t  Enter a specific value or an inclusive range (x, y) for the parameter "
                                      "chosen: ").strip()
                data = SeniorDesign2.filter_materials(data, parameters[list(parameters.keys())[option]], specification)
                del parameters[list(parameters.keys())[option]]
                answer = input(
                    '\n  Would you like to filter further with a different parameter (Y/N)? ')

            errors = []
            for elem in data:
                errors.append(subprocess.run(["python", "SeniorDesign1.py", "./cifs" + date + "/" + elem["material_id"]
                                              + "__" + elem["full_formula"] + ".cif"]))

            for error in errors:
                if error.returncode:
                    print(colored("Conversion Failed. The exit code was: %d" % error.returncode, 'red'))
                    break

            print(colored("Conversion Successful.", 'green'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "3":

            user_input = input('\n  Enter the filename (With the .Vasp extension) to convert to .Cif: ')
            print(colored("\n-------------------------------", 'cyan'))
            SeniorDesign3.convert(user_input.strip(), user_input.strip()[:-5] + ".cif")
            print(colored("Conversion Successful.", 'green'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "4":
            user_input = None
        else:
            print(colored("  Not Valid Choice Try again\n", 'red'))


def change_console_title():
    system("title " + "The All-in-One Physics Tool")


def main():
    change_console_title()
    print_menu()
    print_options()
    input('\n\nPress ENTER to exit')


if __name__ == '__main__':
    main()
