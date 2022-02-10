import sys
from colorama import init
from termcolor import cprint, colored
from pyfiglet import figlet_format
from os import system, scandir
import SeniorDesign1
import SeniorDesign2
import SeniorDesign3
import SeniorDesign5
from datetime import datetime


def print_menu():
    init(strip=not sys.stdout.isatty())
    cprint(figlet_format('AIO Physics Tool'),
           'green', attrs=['bold'])
    print(colored('Tool Created By: Team  3 \n\n', 'cyan'))


def int_input(text, bounds=None):
    ret = q_input(text)
    while True:
        try:
            ret = int(ret)
            if bounds[0] <= ret <= bounds[1]:
                break
        except ValueError:
            pass

        print("Please enter a number within the bounds", bounds)
        ret = q_input(text)

    return ret


def q_input(text=""):
    response = input(text)
    if response.lower().strip() == "q":
        sys.exit(0)

    return response


def groups_input():
    number_groups = int_input('\n  Enter the amount of (Groups of elements): ', (1, 10))
    groups = []
    for i in range(number_groups):
        nput = q_input("  Enter the elements of group " + str(i) + ", separated by a comma (Example: Au,O,Br) : ")
        if " " in nput:
            print(colored("\tPlease enter elements separated by commas instead of spaces (Example: Au,O,Br).\n", "red"))
            return groups_input()
        groups.append([elem.strip().title() for elem in nput.split(",")])

    return groups


def print_options():  # sourcery skip: identity-comprehension, list-comprehension
    user_input = True

    while user_input:
        print(colored('  [1] - .Cif To .Vasp Converter', 'yellow'))
        print(colored('  [2] - Download .Cif files from MaterialsProject.Org', 'yellow'))
        print(colored('  [3] - .Vasp To .Cif Converter', 'yellow'))
        print(colored('  [4] - POTCAR Merge', 'yellow'))
        print(colored('  [5] - Download the Raw data files from nomad-lab.eu', 'yellow'))
        print(colored('  [6] - Exit', 'yellow'))
        print(colored("  Selection: ", 'cyan'), end='')

        user_input = q_input().strip()

        if user_input == "1":

            user_input = q_input('\n  Enter the filename (With the .Cif extension) to convert to .Vasp: ')
            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign1.convert(user_input.strip(), user_input.strip()[:-4] + ".vasp")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "2":

            groups = groups_input()

            print(colored("\n-------------------------------", 'cyan'))
            date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            text = "\tSuccessfully Downloaded .Cif Files, Folder name: /cifs" + date + ", downloaded files:"
            print(colored("Downloading...", 'green'))
            data = SeniorDesign2.download_cif(groups, "./cifs" + date + "/")
            print(colored(text, 'green'))
            for i, elem in enumerate(data):
                print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                              ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

            answer = q_input('\n\n  Would you like to filter then convert the selected .Cif files downloaded to .Vasp '
                           'format (Y/N)? ')
            options = ["formation_energy_per_atom", "full_formula", "e_above_hull", "spacegroup (symbol)",
                       "band_gap", "nsites", "density", "volume"]
            parameters = ["Formation Energy (eV)", "Formula (ex: Cu2I1Br1)", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Band Gap (eV)", "Nsites", "Density", "Volume"]
            parameters = {parameter: option for parameter, option in zip(parameters, options)}

            if answer.strip().lower() != "y":
                print(colored("\n-------------------------------", 'cyan'))
                continue

            print("\n  These are the parameters you can filter materials by:")
            for i, parameter in enumerate(list(parameters.keys())):
                print("\n\t", str(i) + ".", parameter)

            while answer.strip().lower()[0] == "y":
                option = int_input('\n\n  Choose one of the parameters above (enter a number): ',
                                   (0, len(parameters.keys()) - 1))
                specification = q_input("\n\t  Enter a specific value x or an inclusive range x y for the parameter "
                                      "chosen: ").strip()
                data1 = SeniorDesign2.filter_materials(data, parameters[list(parameters.keys())[option]], specification)
                if data1 == 1:
                    print(colored("Please enter a value x or a inclusive range of numbers x y.\n", "red"))
                    continue
                old_data = data
                data = data1

                print(colored("\tSelected CIF files:", "green"))
                for i, elem in enumerate(data):
                    print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                                  ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
                if not data:
                    print(colored("None", "red"))
                print("\n")

                # CANCELING THE FILTERING
                answer = q_input("\n Would you like to cancel this filtering (Y/N)? ")

                if answer.strip().lower()[0] == "y":
                    data = old_data
                    print(colored("\tSelected CIF files:", "green"))
                    for i, elem in enumerate(data):
                        print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                                      ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

                # FILTER FURTHER?
                answer = q_input('\n\n  Would you like to filter further with a different parameter (Y/N)? ')

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

            user_input = q_input('\n  Enter the filename (With the .Vasp extension) to convert to .Cif: ')
            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign3.convert(user_input.strip(), user_input.strip()[:-5] + ".cif")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "4":

            user_input = q_input('\n  Enter the elements separated by a space: ')
            input_elements = [elem.title() for elem in user_input.split(" ")]
            available_elements = [f.name for f in scandir("PBE") if f.is_dir()]
            lst = [elem0.split("_")[0] for elem0 in available_elements]
            elements = []
            error = False

            for elem in input_elements:
                if elem in lst:
                    potential_elements = [elem0 for elem0 in available_elements if elem0.split("_")[0] == elem]
                    if len(potential_elements) == 1:
                        elements.append(potential_elements[0])
                        continue

                    chosen = q_input("\nFor " + colored(elem, "green") + ", choose between: " +
                                   colored("  ".join(potential_elements), "green") + ": ")
                    chosen = chosen[0].upper() + chosen[1:].lower()
                    while chosen not in potential_elements:
                        chosen = q_input("\nInvalid choice, choose between:" +
                                       colored("  ".join(potential_elements), "green") + ": ")
                    elements.append(chosen)

                else:
                    print(colored("\nThe element " + elem + " does not seem to exist in the local database.", "red"))
                    print(colored("\nMerging unsuccessful.\n", "red"))
                    error = True
                    break
            if error:
                continue

            with open("MERGED_POTCAR", "w") as merged:
                for elem in elements:
                    with open("PBE/" + elem + "/POTCAR", "r") as potcar:
                        merged.write(potcar.read())

            print(colored("\nMerging successful. File MERGED_POTCAR created.", "green"))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "5":

            groups = groups_input()

            print(colored("\n-------------------------------", 'cyan'))
            text = "\tSelected materials:"
            print(colored("Loading...", 'green'))
            data = SeniorDesign5.all_possible_materials(groups)
            print(colored(text, 'green'))
            for i, elem in enumerate(data):
                print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
            print('\n')

            options = ["formation_energy_per_atom", "full_formula", "e_above_hull", "spacegroup (symbol)",
                       "band_gap", "nsites", "density", "volume"]
            parameters = ["Formation Energy (eV)", "Formula (ex: Cu2I1Br1)", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Band Gap (eV)", "Nsites", "Density", "Volume"]
            parameters = dict(zip(parameters, options))

            if len(data) > 1:
                print("\n  These are the parameters you can filter materials by, please filter until only one material "
                      "is left:")
                for i, parameter in enumerate(list(parameters.keys())):
                    print("\n\t", str(i) + ".", parameter)

            while len(data) > 1:
                option = int_input('\n\n  Choose one of the parameters above (enter a number): ',
                                   (0, len(parameters.keys()) - 1))
                specification = q_input("\n\t  Enter a specific value x or an inclusive range x y for the parameter "
                                      "chosen: ").strip()
                data1 = SeniorDesign5.filter_materials(data, parameters[list(parameters.keys())[option]], specification)
                if data1 == 1:
                    print(colored("Please enter a value x or a inclusive range of numbers x y.\n", "red"))
                    continue
                old_data = data
                data = data1

                print(colored("\t\nSelected materials:", "green"))
                for i, elem in enumerate(data):
                    print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

                if not data:
                    print(colored("None. Canceling this filtering...\n", "red"))
                    data = old_data

                    print(colored("\tSelected materials:", "green"))
                    for i, elem in enumerate(data):
                        print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
                    print("\n")
                    continue
                print("\n")

                # CANCELING THE FILTERING
                answer = q_input("\n Would you like to cancel this filtering (Y/N)? ")
                print()

                if answer.strip().lower()[0] == "y":
                    data = old_data
                    print(colored("\tSelected CIF files:", "green"))
                    for i, elem in enumerate(data):
                        print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

            print(colored("Downloading the Raw data files...\n", 'green'))

            errors = [
                SeniorDesign5.download_metadata(elem["full_formula"]) for elem in data
            ]

            not_good = False
            for error in errors:
                if error:
                    print(colored("Error. GGA Static Calculation is not available for the selected material."
                                  "The exit code was: %d" % error, 'red'))
                    not_good = True
                    break

            if not not_good:
                print(colored("Downloading Successful.", 'green'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "6":
            return

        else:
            print(colored("  Not Valid Choice Try again\n", 'red'))
            return print_options()


def change_console_title():
    system("title " + "The All-in-One Physics Tool")


def main():
    print("")
    change_console_title()
    print_menu()
    print_options()
    q_input('\n\nPress ENTER to exit')


if __name__ == '__main__':
    main()
