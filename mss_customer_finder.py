#!/bin/python
# Customer Finder
from os import path, walk
from argparse import ArgumentParser


def main():

    LOCATION_CLOUD = '/app/mss/configs/core/public/flat'
    LOCATION_PREMISE = '/app/mss/configs/cpe/public/flat'
    term, location = cli()

    #Default locations based on where they are in mssbastion
    if location is None:
        #for a given location, list out each file recursively
        files_1 = [path.relpath(path.join(dirpath, file), LOCATION_CLOUD) for (
            dirpath, dirnames, filenames) in walk(LOCATION_CLOUD) for file in filenames]
        files_2 = [path.relpath(path.join(dirpath, file), LOCATION_PREMISE) for (
            dirpath, dirnames, filenames) in walk(LOCATION_PREMISE) for file in filenames]
        files = files_1 + files_2
    else:
        files = [path.relpath(path.join(dirpath, file), location) for (
            dirpath, dirnames, filenames) in walk(location) for file in filenames]

    found_a_result = False
    for i in files:
        if location is None:
            try:
                current_file = LOCATION_CLOUD + "/" + i
            except IOError:
                current_file = LOCATION_PREMISE + "/" + i
        else:
            current_file = location + "/" + i
        result, line = file_parser(current_file, term)
        if result is True:
            found_a_result = True
            print("Found customer backup in " + current_file)
            print(line + '\n')

    if found_a_result is False:
        print("Customer not found.  Try a different search term.  Tip: Try to limit searches to one word")


def cli():
    """
    Argument Parser for CLI commands.

    Returns Term, Location (default none)
    """
    parser = ArgumentParser(
        description='Search Level 3 rancid riles for customer VDOMs')
    parser.add_argument('Term', help='An IP address, or the customers name')
    parser.add_argument(
        '-l', '--location', help='Search a custom location besides the default cloud and premise locations', default=None)
    args = parser.parse_args()

    return args.Term, args.location


def file_parser(file_in, term):
    """
    Proivded an open file, searches the file for the term provided.
    """

    try:
        with open(file_in, 'r') as input_file:
            contents = input_file.readlines()
    except IOError:
        return False, None

    # Check a provided term.
    # Transform the text in various ways to try and suss out the correct format
    for line in contents:
        result_untransformed = term in line
        if result_untransformed is False:
            result_upper = term.upper() in line
            if result_upper is False:
                result_lower = term.lower() in line
                if result_lower is False:
                    result_title = term.title() in line
                    if result_title is False:
                        term = term.upper()
                        term = term.replace(" ", "_")
                        result_no_space = term in line
                        if result_no_space is True:
                            return result_no_space, line.split('\"')[1]
                    elif 'comments' in line:
                        return result_title, line.split('\"')[1]
                elif 'comments' in line:
                    return result_lower, line.split('\"')[1]
            elif 'comments' in line:
                return result_upper, line.split('\"')[1]
        elif 'comments' in line:
            return result_untransformed, line.split('\"')[1]

    return False, None

if __name__ == '__main__':
    main()
