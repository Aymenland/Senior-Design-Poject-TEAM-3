from optparse import OptionParser
from cif2vasp import convert


parser = OptionParser()
parser.add_option("-o", "--output", dest="output", help="Save VASP to named file (include format)", metavar="FILE")
(options, args) = parser.parse_args()

if len(args) > 1:
    print("I can only convert one file at a time")
    exit(0)

input_files = (open(args[0], 'r'), args[0])
if options.output:
    vasp_file = options.output
else:
    vasp_file = args[0][:-4] + ".vasp"

try:
    convert(input_files[1], vasp_file)
except:
    exit(1)
