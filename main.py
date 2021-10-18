import sys
from colorama import init
from termcolor import cprint, colored
from pyfiglet import figlet_format
from os import system
import subprocess


def print_menu():
    init(strip=not sys.stdout.isatty())
    cprint(figlet_format('AIO Physics Tool'),
           'green', attrs=['bold'])
    print(colored('Tool Created By: Team  3 \n\n', 'cyan'))


def print_options():
    user_input = True

    while user_input:
        print(colored('  [1] - .Cif To .Vasp Converter', 'yellow'))
        print(colored('  [4] - Exit Tool', 'yellow'))
        print(colored("  Selection: ", 'cyan'), end='')

        user_input = input()

        if user_input == "1":
            user_input = input('\n  Enter the filename (without the .Cif extension) to convert to .Vasp:  ')

            print(colored("\n-------------------------------", 'cyan'))
            list_files = subprocess.run(["python", "SeniorDesign1.py", user_input.strip()])

            if not list_files.returncode:
                print(colored("Conversion Successful.", 'green'))
            else:
                print(colored("Conversion Failed. The exit code was: %d" % list_files.returncode, 'red'))

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
