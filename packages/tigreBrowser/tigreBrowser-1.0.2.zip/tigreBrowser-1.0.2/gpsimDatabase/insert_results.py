#! /usr/bin/env python
import sys
from optparse import OptionParser, OptionGroup
from gpsim_database import *
from datetime import date

ROOT_EXPERIMENT_SET = 'All experiments'

LOOP_TFS = 1

def is_header_line(line, columns):
    try:
        for col in columns:
            if col != None:
                float(line[col])
        return False
    except ValueError:
        return True

def main():
    usage = "usage: %prog [options] database_file dataset_name experiment_name regulator_name experiment_figure"
    parser = OptionParser(usage)
    group_exp = OptionGroup(parser, "Experiment annotation")
    group_data = OptionGroup(parser, "Expression dataset annotation")
    group_figure = OptionGroup(parser, "Figure annotation")

    parser.add_option('-f', '--file', dest='filename',
            help='read data from FILENAME instead of stdin')
    parser.add_option('--log-likelihood-column', dest='log_column', type='int',
            action='store', help='log likelihood column in results [default: %default]', default=2)
    parser.add_option('--baseline-log-likelihood-column', dest='baseline_column', type='int',
            action='store', help='baseline log likelihood column in results (0=no results) [default: %default]', default=0)
    parser.add_option('-d', '--delimiter', dest='delimiter', type='string',
            action='store', help='column delimiter [default: whitespace]', default=None)

    group_exp.add_option('-m', '--model-translation', dest='model_translation',
            action='store_true', help='set model translation to TRUE [default: False]', default=False)
    group_exp.add_option('-l', '--loop-variable', dest='loop_variable', type='int',
            action='store', help='set loop variable [default: %default]', default=2)
    group_exp.add_option('--targets-file', dest='targets_file', type='string',
            action='store', help='set filename of target genes, this must be set if loop variable is se to %d' % LOOP_TFS, default=None)
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

    group_figure.add_option('--figure-name', dest='figure_name', type='string',
            action='store', help='set experiment figure name')
    group_figure.add_option('--figure-desc', dest='figure_desc', type='string',
            action='store', help='set experiment figure description')


    parser.add_option_group(group_exp)
    parser.add_option_group(group_data)
    parser.add_option_group(group_figure)

    (options, args) = parser.parse_args()

    if len(args) < 4:
        print('Not enough arguments. Use -h to show help.')
        sys.exit()

    database_file = args[0]
    dataset_name = args[1]
    experiment_name = args[2]
    regulator_name = args[3] if options.loop_variable != LOOP_TFS else None
    figure_filename = args[4] if len(args) > 4 else None

    dataset_annotation = [dataset_name, options.dataset_species, options.dataset_source, options.dataset_platform, options.dataset_desc, options.dataset_save_location, options.dataset_figure_filename]
    if not options.experiment_desc:
        options.experiment_desc = experiment_name
    experiment_annotation = [regulator_name, options.loop_variable, options.model_translation, options.number_of_params, options.parameter_names, options.producer, options.timestamp, options.experiment_desc, experiment_name]

    figure_annotation = [figure_filename, options.figure_name, options.figure_desc, 0]

    targets_file = options.targets_file
    if not targets_file and options.loop_variable == LOOP_TFS:
        print('Targets filename must be set when loop variable is 1')

    db = gpsim_database(database_file)

    try:
        print('Trying to create tables...')
        db.create_tables()
        print('Tables created')
    except sqlite3.OperationalError:
        print('Tables already exist')

    baseline_col = options.baseline_column - 1 if options.baseline_column != 0 else None

    probe_names, log_likelihoods, baseline_log_likelihoods = get_results(options.filename, options.log_column - 1, baseline_col, options.delimiter)

    params = [None] * len(probe_names)
    db.add_experiment_results(probe_names, log_likelihoods, baseline_log_likelihoods, params, experiment_annotation, dataset_annotation)

    if figure_filename:
        db.add_figure(experiment_annotation, dataset_annotation, figure_annotation)

    if options.experiment_set:
        db.add_experiment_set(options.experiment_set, ROOT_EXPERIMENT_SET, [experiment_annotation], [dataset_annotation])
    else: # put all experiments under ROOT_EXPERIMENT_SET
        db.add_experiment_set(ROOT_EXPERIMENT_SET, None, [experiment_annotation], [dataset_annotation])


    if targets_file:
        targets = []
        for line in open(targets_file):
            targets.append(line.strip())
        db.add_target_sets(targets, experiment_annotation, dataset_annotation)


def get_results(file, log_column, baseline_column, delimiter):
    probe_names = []
    log_likelihoods = []
    baseline_log_likelihoods = []

    def add_results(line):
        line = line.strip().split(delimiter)
        if is_header_line(line, [log_column, baseline_column]):
            return

        probe_names.append(line[0].strip())
        log_likelihoods.append(float(line[log_column]))
        if baseline_column:
            baseline_log_likelihoods.append(float(line[baseline_column]))
        else:
            baseline_log_likelihoods.append(None)

    if not file:
        for line in sys.stdin.readlines():
            add_results(line)
    else:
        for line in open(file):
            add_results(line)
    return probe_names, log_likelihoods, baseline_log_likelihoods


if __name__ == "__main__":
    main()

