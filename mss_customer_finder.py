#!/bin/python3
# Customer Finder

from os import path, walk
from ipaddress import IPv4Network
from argparse import ArgumentParser


def main():

    term, location = cli()

    #Default locations based on where they are in mssbastion
    if location is None:
        location = {'cloud': '/app/mss/configs/core/public',
                    'premise': '/app/mss/configs/cpe/public'}
    else:
        location = location

    #for a given location, list out each file recursively
    files = [path.relpath(path.join(dirpath, file), location) for (
        dirpath, dirnames, filenames) in walk(location) for file in filenames]

    found_a_result = False
    for i in files:
        current_file = location + "/" + i
        result = file_parser(current_file, term)
        if result is True:
            found_a_result = True
            print("Found customer in " + current_file)

    if found_a_result is False:
        print("Customer not found.  Try a different search term")


def cli():
    """
    Argument Parser for CLI commands.

    Returns Term, Location (default none)
    """
    parser = ArgumentParser(
        description='Search Level 3 rancid riles for customer VDOMs')
    parser.add_argument('Term', help='An IP address, or the customers name')
    parser.add_argument(
        '-l', '--location', help='Search a custom location besides the default premise and cloud locations', default=None)
    args = parser.parse_args()

    return args.Term, args.location


def file_parser(file_in, term):
    """
    Proivded an open file, searches the file for the term provided.
    """

    with open(file_in, 'r') as input_file:
        contents = input_file.read()

    # Check a provided term.
    # Transform the text in various ways to try and suss out the correct format
    result_untransformed = term in contents
    if result_untransformed is False:
        result_lower = term.lower() in contents
        if result_lower is False:
            result_upper = term.upper() in contents
            if result_upper is False:
                result_title = term.title() in contents
                if result_title is False:
                    term = term.upper()
                    term = term.replace(" ", "_")
                    result_no_space = term in contents
                    if result_no_space is True:
                        return result_no_space
                else:
                    return result_title
            else:
                return result_upper
        else:
            return result_lower
    else:
        return result_untransformed

    return False

if __name__ == '__main__':
    main()
