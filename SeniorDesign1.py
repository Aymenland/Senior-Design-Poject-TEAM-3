from optparse import OptionParser
from math import cos, sin, sqrt, radians

parser = OptionParser()
parser.add_option("-o", "--output", dest="output", help="Save VASP to named file (include format)", metavar="FILE")
(options, args) = parser.parse_args()

if len(args) > 1:
    print("I can only convert one file at a time")
    exit(0)

input_files = (open(args[0] + ".cif", 'r'), args[0])
if options.output:
    vasp_file = open(options.output, 'w')
else:
    vasp_file = open(args[0] + ".vasp", 'w')

file_lines = input_files[0].readlines()

lines = file_lines[3: 9]
lines = [float(line.split(" ")[-1]) for line in lines]
a, b, c, alpha, beta, gamma = lines
alpha, beta, gamma = radians(alpha), radians(beta), radians(gamma)

a1 = a
a21 = b * cos(gamma)
a22 = b * sin(gamma)
a31 = c * cos(beta)
a32 = c * (cos(alpha) - cos(beta) * cos(gamma)) / sin(gamma)
a33 = sqrt((c ** 2) - (a31 ** 2) - (a32 ** 2))


def setw(s, width):
    s1 = str(s)
    return " " * (width - len(s1)) + s1


vasp_file.write("1\n1.0\n")
vasp_file.write(setw("%.10f" % a1, 20) + " " + setw("%.10f" % 0, 20) + " " + setw("%.10f" % 0, 20) + "\n")
vasp_file.write(setw("%.10f" % a21, 20) + " " + setw("%.10f" % a22, 20) + " " + setw("%.10f" % 0, 20) + "\n")
vasp_file.write(setw("%.10f" % a31, 20) + " " + setw("%.10f" % a32, 20) + " " + setw("%.10f" % a33, 20) + "\n")


lines = file_lines[26:]
lines = [line for line in lines if line.strip()]
lines = [[word for word in line.split(" ") if word][0] for line in lines]
lines_no_dups = []
for line in lines:
    if line not in lines_no_dups:
        lines_no_dups.append(line)

elements = {elem: lines.count(elem) for elem in lines_no_dups}


for element in lines_no_dups:
    vasp_file.write(setw(element, 5))
vasp_file.write("\n")
for element in lines_no_dups:
    vasp_file.write(setw(elements[element], 5))


vasp_file.write("\nDirect\n")
lines = file_lines[26:]
lines = [line for line in lines if line.strip()]
lines = [[word for word in line.split(" ") if word][3: 6] for line in lines]


for line in lines:
    vasp_file.write(setw("%.9f" % float(line[0]), 16) + "    " + setw("%.9f" % float(line[1]), 16) + "    " +
                    setw("%.9f" % float(line[2]), 16) + "\n")
