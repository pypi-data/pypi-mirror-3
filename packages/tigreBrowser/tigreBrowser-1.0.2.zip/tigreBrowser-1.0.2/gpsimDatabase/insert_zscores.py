#! /usr/bin/env python
import sys
from optparse import OptionParser, OptionGroup
from gpsim_database import *

def is_header_line(line, columns):
    try:
        for col in columns:
            if col != None:
                float(line[col])
        return False
    except ValueError:
        return True

def main():
    usage = "usage: %prog [options] database_file dataset_name"
    parser = OptionParser(usage)
    group_data = OptionGroup(parser, "Expression dataset annotation")

    parser.add_option('-f', '--file', dest='filename',
            help='read data from FILENAME instead of stdin')
    parser.add_option('-c', '--column', dest='column', type='int',
            action='store', help='data column [default: %default]', default=2)
    parser.add_option('-d', '--delimiter', dest='delimiter', type='string',
            action='store', help='column delimiter [default: whitespace]', default=None)

    group_data.add_option('--dataset-desc', dest='dataset_desc', type='string',
            action='store', help='set dataset description')
    group_data.add_option('--species', dest='dataset_species', type='string',
            action='store', help='set dataset species')
    group_data.add_option('--source', dest='dataset_source', type='string',
            action='store', help='set dataset source')
    group_data.add_option('--platform', dest='dataset_platform', type='string',
            action='store', help='set dataset platform')
    group_data.add_option('--save-location', dest='dataset_save_location', type='string',
            action='store', help='set dataset save location')
    group_data.add_option('--figure-filename', dest='dataset_figure_filename', type='string',
            action='store', help='set dataset figure filename')

    parser.add_option_group(group_data)

    (options, args) = parser.parse_args()

    if len(args) < 2:
        print('Not enough arguments. Use -h to show help.')
        sys.exit()

    database_file = args[0]
    dataset_name = args[1]
    dataset_annotation = [dataset_name, options.dataset_species, options.dataset_source, options.dataset_platform, options.dataset_desc, options.dataset_save_location, options.dataset_figure_filename]

    db = gpsim_database(database_file)

    try:
        print('Trying to create tables...')
        db.create_tables()
        print('Tables created')
    except sqlite3.OperationalError:
        print('Tables already exist')

    probe_names, data = get_data(options.filename, options.column - 1, options.delimiter)
    db.add_zscores(probe_names, data, dataset_annotation)

def get_data(file, column, delim):
    probe_names = []
    data = []

    def add_data(line):
        line = line.strip().split(delim)
        if is_header_line(line, [column]):
            return

        probe_names.append(line[0].strip())
        data.append(float(line[column]))

    if not file:
        for line in sys.stdin.readlines():
            add_data(line)
    else:
        for line in open(file):
            add_data(line)
    return probe_names, data


if __name__ == "__main__":
    main()
