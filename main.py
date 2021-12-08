import sys
from colorama import init
from termcolor import cprint, colored
from pyfiglet import figlet_format
from os import system
import SeniorDesign1
import SeniorDesign2
import SeniorDesign3
from datetime import datetime


def print_menu():
    init(strip=not sys.stdout.isatty())
    cprint(figlet_format('AIO Physics Tool'),
           'green', attrs=['bold'])
    print(colored('Tool Created By: Team  3 \n\n', 'cyan'))


def int_input(text, bounds=None):
    ret = input(text)
    while True:
        try:
            ret = int(ret)
            if bounds[0] <= ret <= bounds[1]:
                break
        except ValueError:
            pass

        print("Please enter a number within the bounds", bounds)
        ret = input(text)

    return ret


def print_options():
    user_input = True

    while user_input:
        print(colored('  [1] - .Cif To .Vasp Converter', 'yellow'))
        print(colored('  [2] - Download .Cif files from MaterialsProject.Org', 'yellow'))
        print(colored('  [3] - .Vasp To .Cif Converter', 'yellow'))
        print(colored('  [4] - Exit', 'yellow'))
        print(colored("  Selection: ", 'cyan'), end='')

        user_input = input().strip()

        if user_input == "1":

            user_input = input('\n  Enter the filename (With the .Cif extension) to convert to .Vasp: ')
            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign1.convert(user_input.strip(), user_input.strip()[:-4] + ".vasp")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "2":

            number_groups = int_input('\n  Enter the amount of (Groups of elements): ', (1, 10))
            groups = []
            for i in range(number_groups):
                groups.append([elem.strip().title() for elem in
                               input("  Enter the the elements of group " + str(i) +
                                     ", separated by a comma (Example: Au,O,Br) : ").split(",")])

            print(colored("\n-------------------------------", 'cyan'))
            date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            text = "\tSuccessfully Downloaded .Cif Files, Folder name: /cifs" + date + ", downloaded files:"
            print(colored("Downloading...", 'green'))
            data = SeniorDesign2.download_cif(groups, "./cifs" + date + "/")
            print(colored(text, 'green'))
            for i, elem in enumerate(data):
                print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                              ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

            answer = input('\n  Would you like to convert some of the .Cif files downloaded to .Vasp format (Y/N)? ')
            options = ["formation_energy_per_atom", "full_formula", "e_above_hull", "spacegroup (symbol)",
                       "band_gap", "nsites", "density", "volume"]
            parameters = ["Formation Energy (eV)", "Formula (ex: Cu2I1Br1)", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Band Gap (eV)", "Nsites", "Density", "Volume"]
            parameters = {parameter: option for parameter, option in zip(parameters, options)}

            if answer.strip().lower() == "n":
                print(colored("\n-------------------------------", 'cyan'))
                continue

            print("\n  These are the parameters you can filter materials by:")
            for i, parameter in enumerate(list(parameters.keys())):
                print("\n\t", str(i) + ".", parameter)

            while answer.strip().lower() == "y":
                option = int_input('\n\n  Choose one of the parameters above (enter a number): ',
                                   (0, len(parameters.keys()) - 1))
                specification = input("\n\t  Enter a specific value x or an inclusive range x y for the parameter "
                                      "chosen: ").strip()
                data1 = SeniorDesign2.filter_materials(data, parameters[list(parameters.keys())[option]], specification)
                if data1 == 1:
                    print(colored("Please enter a value x or a inclusive range of numbers x y.\n", "red"))
                    continue
                data = data1

                print(colored("\tSelected CIF files:", "green"))
                for i, elem in enumerate(data):
                    print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                                  ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
                if not data:
                    print(colored("None", "red"))
                print("\n")

                answer = input('\n  Would you like to filter further with a different parameter (Y/N)? ')

            errors = []
            for elem in data:
                errors.append(SeniorDesign1.convert("./cifs" + date + "/" + elem["material_id"]
                                                    + "__" + elem["full_formula"] + ".cif", "./cifs" + date + "/"
                                                    + elem["material_id"] + "__" + elem["full_formula"] + ".vasp"))

            not_good = False
            for error in errors:
                if error:
                    print(colored("Conversion Failed. The exit code was: %d" % error, 'red'))
                    not_good = True
                    break

            if not not_good:
                print(colored("Conversion Successful.", 'green'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "3":

            user_input = input('\n  Enter the filename (With the .Vasp extension) to convert to .Cif: ')
            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign3.convert(user_input.strip(), user_input.strip()[:-5] + ".cif")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "4":
            return
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
