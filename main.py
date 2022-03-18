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
from tabulate import tabulate


def print_menu():
    init(strip=not sys.stdout.isatty())
    cprint(figlet_format('AIO Physics Tool'),
           'green', attrs=['bold'])
    print(colored('Tool Created By: Team  3 \n\n', 'cyan'))


def int_input(text, bounds=None):
    ret = input(text)
    if ret.lower().strip() == "q":
        return -1

    while True:
        try:
            ret = int(ret)
            if bounds[0] <= ret <= bounds[1]:
                break
        except ValueError:
            pass

        print("Please enter a number within the bounds", bounds)
        ret = input(text)
        if ret.lower().strip() == "q":
            return -1

    return ret


def groups_input():
    number_groups = int_input('\n  Enter the amount of (Groups of elements): ', (1, 10))
    if number_groups == -1:
        return 0

    groups = []
    for i in range(number_groups):
        nput = input("  Enter the elements of group " + str(i) + ", separated by a comma (Example: Au,O,Br) : ")
        if nput.lower().strip() == "q":
            return 0

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

        user_input = input().strip()
        if user_input.lower().strip() == "q":
            return print_options()

        if user_input == "1":

            user_input = input('\n  Enter the filename (With the .Cif extension) to convert to .Vasp: ')
            if user_input.lower().strip() == "q":
                return print_options()

            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign1.convert(user_input.strip(), user_input.strip()[:-4] + ".vasp")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "2":

            groups = groups_input()
            if groups == 0:
                return print_options()

            print(colored("\n-------------------------------", 'cyan'))
            date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            text = "\tSuccessfully Downloaded .Cif Files, Folder name: /cifs" + date + ", downloaded files:"
            print(colored("Downloading...", 'green'))
            data = SeniorDesign2.download_cif(groups, "./cifs" + date + "/")
            if data == 1:
                print(colored("Input Error.\n", "red"))
                continue

            print(colored(text, 'green'))
            for i, elem in enumerate(data):
                print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                              ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

            answer = input('\n\n  Would you like to filter then convert the selected .Cif files downloaded to .Vasp '
                           'format (Y/N)? ')
            if answer.lower().strip() == "q":
                return print_options()

            if answer.strip().lower() != "y":
                print(colored("\n-------------------------------", 'cyan'))
                continue

            options = ["formation_energy_per_atom", "full_formula", "e_above_hull", "spacegroup (symbol)",
                       "density"]
            parameters = ["Formation Energy (eV)", "Formula (ex: Cu2I1Br1)", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Density"]

            print("\n",
                  tabulate([[i] + [elem[option] if option != "spacegroup (symbol)" else elem["spacegroup"]["symbol"]
                                   for option in options] for i, elem in enumerate(data)], headers=[""] + parameters),
                  end="\n\n")

            while answer.strip().lower()[0] == "y":

                selections = input("\nSelect materials from the table above by their number (0 - " + str(len(data) - 1)
                                   + ") separated by commas: ")
                if selections.strip().lower() == "q":
                    return print_options()

                old_data = data
                data = [data[int(elem.strip())] for elem in selections.split(",")]

                print(colored("\tSelected CIF files:", "green"))
                for i, elem in enumerate(data):
                    print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                                  ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
                if not data:
                    print(colored("None", "red"))
                print("\n")

                # CANCELING THE FILTERING
                answer = input("\n Would you like to cancel this filtering (Y/N)? ")
                if answer.lower().strip() == "q":
                    return print_options()

                if answer.strip().lower()[0] == "y":
                    data = old_data
                    print(colored("\tSelected CIF files:", "green"))
                    for i, elem in enumerate(data):
                        print(colored(elem["material_id"] + "__" + elem["full_formula"] + ".cif" +
                                      ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

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
            if user_input.lower().strip() == "q":
                return print_options()

            print(colored("\n-------------------------------", 'cyan'))
            return_code = SeniorDesign3.convert(user_input.strip(), user_input.strip()[:-5] + ".cif")
            if not return_code:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion unsuccessful.", 'red'))
            print(colored("-------------------------------\n", 'cyan'))

        elif user_input == "4":

            nput = input('\n  Enter the elements separated by a space: ')
            if nput.lower().strip() == "q":
                return print_options()

            input_elements = [elem.title() for elem in nput.split(" ")]
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

                    chosen = input("\nFor " + colored(elem, "green") + ", choose between: " +
                                   colored("  ".join(potential_elements), "green") + ": ")
                    if chosen.lower().strip() == "q":
                        return print_options()

                    chosen = chosen[0].upper() + chosen[1:].lower()
                    while chosen not in potential_elements:
                        chosen = input("\nInvalid choice, choose between:" +
                                       colored("  ".join(potential_elements), "green") + ": ")
                        if chosen.lower().strip() == "q":
                            return print_options()

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
            if groups == 0:
                return print_options()

            print(colored("\n-------------------------------", 'cyan'))
            text = "\tSelected materials:"
            print(colored("Loading...", 'green'))
            data = SeniorDesign5.all_possible_materials(groups)
            if data == 1:
                print(colored("Input Error.\n", "red"))
                continue

            print(colored(text, 'green'))
            for i, elem in enumerate(data):
                print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")
            print('\n')

            options = ["formation_energy_per_atom", "full_formula", "e_above_hull", "spacegroup (symbol)",
                       "density"]
            parameters = ["Formation Energy (eV)", "Formula (ex: Cu2I1Br1)", "E Above Hull (eV)", "Spacegroup (Symbol)",
                          "Density"]

            print("\n",
                  tabulate([[i] + [elem[option] if option != "spacegroup (symbol)" else elem["spacegroup"]["symbol"]
                                   for option in options] for i, elem in enumerate(data)], headers=[""] + parameters),
                  end="\n\n")

            answer = 'y'
            while answer.strip().lower()[0] == "y":

                selections = input("\nSelect one material from the table above by its number (0 - " + str(len(data) - 1)
                                   + "): ").strip()
                if selections.strip().lower() == "q":
                    return print_options()

                old_data = data
                data = [data[int(selections)]]

                print(colored("\tSelected materials:", "green"))
                for i, elem in enumerate(data):
                    print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

                if not data:
                    print(colored("None", "red"))
                print('\n')

                # CANCELING THE FILTERING
                answer = input("\n Would you like to cancel this filtering (Y/N)? ")
                if answer.lower().strip() == "q":
                    return print_options()

                if answer.strip().lower()[0] == "y":
                    data = old_data
                    print(colored("\tSelected materials:", "green"))
                    for i, elem in enumerate(data):
                        print(colored(elem["full_formula"] + ("\n" if (i % 4) == 3 else "\t"), "green"), end="")

            print(colored("Downloading the Raw data files...\n", 'green'))

            errors = [
                SeniorDesign5.download_metadata(elem["material_id"], elem["full_formula"]) for elem in data
            ]

            not_good = False
            for error in errors:
                if error:
                    print(colored("Error. GGA Static Calculation is not available for the selected material."
                                  "The exit code was: %d" % error, 'red'))
                    not_good = True
                    break

            input_elements = data[0]["elements"]
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

                    chosen = input("\nFor " + colored(elem, "green") + ", choose between: " +
                                   colored("  ".join(potential_elements), "green") + ": ")
                    if chosen.lower().strip() == "q":
                        return print_options()

                    chosen = chosen[0].upper() + chosen[1:].lower()
                    while chosen not in potential_elements:
                        chosen = input("\nInvalid choice, choose between:" +
                                       colored("  ".join(potential_elements), "green") + ": ")
                        if chosen.lower().strip() == "q":
                            return print_options()

                    elements.append(chosen)

                else:
                    print(colored("\nThe element " + elem + " does not seem to exist in the local database.", "red"))
                    print(colored("\nMerging unsuccessful.\n", "red"))
                    error = True
                    break
            if error:
                continue

            with open(data[0]["full_formula"] + "/" + data[0]["full_formula"] + " - SubFolder 2/MERGED_POTCAR", "w") as merged:
                for elem in elements:
                    with open("PBE/" + elem + "/POTCAR", "r") as potcar:
                        merged.write(potcar.read())

            if not not_good:
                print(colored("\nDownloading Successful.", 'green'))

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
    input('\n\nPress ENTER to exit')


if __name__ == '__main__':
    main()
