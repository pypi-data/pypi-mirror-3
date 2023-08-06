import sys
import re
from subprocess import Popen, PIPE

UNIT_SIZE = {
    'K': 1,
    'M': 1024,
    'G': 1024 ** 2,
    'T': 1024 ** 3,
}


def get_sizes(args=None):
    """Run du -h with any optional parameters and sort its output.

    :param args: A list of parameters to pass to du

    :returns: A list of tuples (filename, size).

    """
    command = " ".join(["du", "-h"] + (args if args else []))
    process = Popen(command, stdout=PIPE, shell=True)
    output = process.stdout.read()
    lines = output.split("\n")
    regex = re.compile("^\s*(\S+)\s+(.*)")
    pairs = []
    for l in lines:
        f = regex.findall(l)
        if f:
            pairs.append([f[0][1], f[0][0]])
    return pairs


def size_to_kb(size):
    """Parses a size of the format <number><unit> and returns it in kb."""
    number = float(size[:-1])
    unit = size[-1]
    return number * UNIT_SIZE[unit]


def du_tuple_cmp(a, b):
    """Compare two tuples as returned by get_sizes."""
    return cmp(size_to_kb(a[1]), size_to_kb(b[1]))


def size_sort(file_size):
    """Sorts a list of tuples (filename, size) by size."""
    return sorted(file_size, cmp=du_tuple_cmp)


def duh():
    """Run du -h with any extra parameters in the command line and sort
    the output by size.

    """
    file_sizes = size_sort(get_sizes(sys.argv[1:]))
    for filename, size in file_sizes:
        print size, "\t", filename
