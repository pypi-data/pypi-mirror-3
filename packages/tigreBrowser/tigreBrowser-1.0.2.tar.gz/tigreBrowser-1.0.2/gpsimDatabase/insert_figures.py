#! /usr/bin/env python
import sys
from optparse import OptionParser, OptionGroup
from gpsim_database import *
from datetime import date

def main():
    usage = "usage: %prog [options] database_file experiment_name regulator_name dataset_name"
    parser = OptionParser(usage)
    group_exp = OptionGroup(parser, "Experiment annotation")
    group_data = OptionGroup(parser, "Expression dataset annotation")

    parser.add_option('-f', '--file', dest='filename',
            help='read data from FILENAME instead of stdin')
    parser.add_option('-d', '--delimiter', dest='delimiter', type='string',
            action='store', help='column delimiter [default: whitespace]', default=None)

    group_exp.add_option('-m', '--model-translation', dest='model_translation',
            action='store_true', help='set model translation to TRUE [default: False]', default=False)
    group_exp.add_option('-l', '--loop-variable', dest='loop_variable', type='int',
            action='store', help='set loop variable [default: %default]', default=2)
    group_exp.add_option('--number-of-params', dest='number_of_params', type='int',
            action='store', help='set the number of experiment parameters')
    group_exp.add_option('--parameter-names', dest='parameter_names', type='string',
            action='store', help='set the experiment parameter names')
    group_exp.add_option('-p', '--producer', dest='producer', type='string',
            action='store', help='set the experiment producer')
    group_exp.add_option('-t', '--timestamp', dest='timestamp', type='string',
            action='store', help='set the experiment timestamp YYYY-MM-DD [default: current date]', default=date.today().isoformat())
    group_exp.add_option('--experiment-desc', dest='experiment_desc', type='string',
            action='store', help='set experiment description')
    group_exp.add_option('--experiment-set', dest='experiment_set', type='string',
            action='store', help='add results to this experiment set')

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

    parser.add_option_group(group_exp)
    parser.add_option_group(group_data)

    (options, args) = parser.parse_args()

    if len(args) < 3:
        print('Not enough arguments. Use -h to show help.')
        sys.exit()

    database_file = args[0]
    experiment_name = args[1]
    regulator_name = args[2]
    dataset_name = args[3]
    
    experiment_annotation = [regulator_name, options.loop_variable, options.model_translation, options.number_of_params, options.parameter_names, options.producer, options.timestamp, options.experiment_desc, experiment_name]
    dataset_annotation = [dataset_name, options.dataset_species, options.dataset_source, options.dataset_platform, options.dataset_desc, options.dataset_save_location, options.dataset_figure_filename]

    db = gpsim_database(database_file)

    try:
        print('Trying to create tables...')
        db.create_tables()
        print('Tables created')
    except sqlite3.OperationalError:
        print('Tables already exist')

    figure_annotations = get_figures(options.filename, options.delimiter)
    for annotation in figure_annotations:
        db.add_figure(experiment_annotation, dataset_annotation, annotation)

def get_figures(file, delim):
    figures = []
    
    def add_figure(line):
        line = line.strip().split(delim)
        annotation = [line[0].strip(), None, None, None]
        try:
            annotation[1] = line[1].strip()
            annotation[2] = line[2].strip()
            annotation[3] = int(line[3])
        except:
            pass
        figures.append(annotation)

    if not file:
        for line in sys.stdin.readlines():
            add_figure(line)
    else:
        for line in open(file):
            add_figure(line)
    return figures

if __name__ == "__main__":
    main()
