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
    usage = "usage: %prog [options] database_file supplementary_data_name"
    parser = OptionParser(usage)
    group_supp = OptionGroup(parser, "Supplementary dataset annotation")

    parser.add_option('-f', '--file', dest='filename',
            help='read data from FILENAME instead of stdin')
    parser.add_option('-c', '--column', dest='column', type='int',
            action='store', help='data column [default: %default]', default=2)
    parser.add_option('-d', '--delimiter', dest='delimiter', type='string',
            action='store', help='column delimiter [default: whitespace]', default=None)

    group_supp.add_option('-t', '--type', dest='type', type='int',
            action='store', help='set data type (0=boolean, 1=integer, 2=float) [default: 0]', default=0)
    group_supp.add_option('--tf', dest='tf', type='string',
            action='store', help='set TF if this data depends on a TF')
    group_supp.add_option('--source', dest='source', type='string',
            action='store', help='set supplementary data source')
    group_supp.add_option('--plaftorm', dest='platform', type='string',
            action='store', help='set supplementary data platform')
    group_supp.add_option('--desc', dest='desc', type='string',
            action='store', help='set supplementary data desc')

    parser.add_option_group(group_supp)

    (options, args) = parser.parse_args()

    if len(args) < 2:
        print('Not enough arguments. Use -h to show help.')
        sys.exit()

    database_file = args[0]
    name = args[1]
    if not options.desc:
        options.desc = name
    annotation = [options.type, name, options.tf, options.source, options.platform, options.desc]

    db = gpsim_database(database_file)

    try:
        print('Trying to create tables...')
        db.create_tables()
        print('Tables created')
    except sqlite3.OperationalError:
        print('Tables already exist')

    probe_names, data = get_data(options.filename, options.column - 1, options.delimiter)
    db.add_supplementary_data(probe_names, data, annotation)

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
