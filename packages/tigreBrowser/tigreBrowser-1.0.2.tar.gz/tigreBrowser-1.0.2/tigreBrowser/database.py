#! /usr/bin/env python

import sqlite3

class Database:
    """GPSIM database access for results browser.
    """

    def __init__(self, sqlite_file):
        """Connects to a given database file.
        """
        self.conn = sqlite3.connect(sqlite_file)
        self.c = self.conn.cursor()

    def __del__(self):
        """Closes the database connection and commits any transactions.
        """
        self.conn.commit()
        self.c.close()
        self.conn.close()

    def __to_placeholders(self, values):
        return ''.join(['null,' if x == None else '?,' for x in values]).strip(',')

    def __get_experiment_ids_in_sets(self, set_ids):
        self.c.execute("""SELECT DISTINCT se.experiment_id
                          FROM experiment_set_experiments AS se
                          WHERE se.experiment_set_id IN (%s)""" % self.__to_placeholders(set_ids), set_ids)
        return [id for (id,) in self.c.fetchall()]

    def __get_experiment_sets_children(self, set_ids):
        self.c.execute("""SELECT DISTINCT s.experiment_set_id
                          FROM experiment_set AS s
                          WHERE s.parent_id IN (%s)""" % self.__to_placeholders(set_ids), set_ids)
        return [id for (id,) in self.c.fetchall()]

    def __create_supplementary_data_query(self, id, symbol, value, gene_ids=None):
        if not gene_ids:
            query = """SELECT supp.gene_id
                       FROM supplementary_data AS supp
                       WHERE supp.supp_dataset_id = ?
                         AND supp.value %s ?""" % symbol
            args = [id, value]
        else:
            query = """SELECT supp.gene_id
                       FROM supplementary_data AS supp
                       WHERE supp.supp_dataset_id = ?
                         AND supp.value %s ?
                         AND supp.gene_id IN (%s)""" % (symbol, self.__to_placeholders(gene_ids))
            args = [id, value] + gene_ids

        return query, args

    def __create_supplementary_data_queries(self, supp_options, supp_ids):
        query = []
        args = []
        for (name, symbol, value) in supp_options:
            q, a = self.__create_supplementary_data_query(supp_ids[name], symbol, float(value))
            query.append(q)
            args += a
        return '\nINTERSECT\n'.join(query), args

    def __create_log_likelihood_filter(self, criteria, experiment_id, diff=False):
        query = """SELECT r.gene_id
                   FROM results AS r
                   WHERE r.experiment_id = ?"""
        args = [experiment_id]

        if diff:
            q = ' AND (r.log_likelihood - r.baseline_log_likelihood) %s ? '
        else:
            q = ' AND r.log_likelihood %s ? '

        for (symbol, value) in criteria:
            query += q % symbol
            args.append(value)

        return query, args

    def __create_baseline_filter(self, criteria, experiment_id):
        query = """SELECT DISTINCT r.gene_id
                   FROM results AS r
                   WHERE r.experiment_id = ?"""
        args = [experiment_id]

        q = ' AND r.baseline_log_likelihood %s ? '
        for (symbol, value) in criteria:
            query += q % symbol
            args.append(value)

        return query, args

    def __create_z_score_filter(self, criteria):
        query = """SELECT z.gene_id
                   FROM z_scores AS z
                   WHERE 1"""
        args = []

        q = ' AND z.mean_z_score %s ? '
        for (symbol, value) in criteria:
            query += q % symbol
            args.append(value)

        return query, args

    def __create_filter(self, filterby, criteria, experiment_id, baseline=False, diff=False):
        if baseline:
            return self.__create_baseline_filter(criteria, experiment_id)
        elif filterby == 'zscore':
            return self.__create_z_score_filter(criteria)
        else:
            return self.__create_log_likelihood_filter(criteria, experiment_id, diff)

    def get_experiment_ids_in_set_recursively(self, set_id):
        """Get all experiment ids that belong to the given experiment set or any subset of it.

        Returns: [experiment id]
        """
        ids = []
        children = [set_id]
        while len(children) > 0:
            ids.extend(self.__get_experiment_ids_in_sets(children))
            children = self.__get_experiment_sets_children(children)

        return ids

    def get_experiment_sets(self):
        """Gets all experiment sets.

        Returns: [(set name, set id, set parent id)]
        """
        self.c.execute("""SELECT s.name, s.experiment_set_id, s.parent_id
                          FROM experiment_set AS s""")
        return self.c.fetchall()

    def get_experiment_set_id(self, set_name):
        """Gets the id of the given experiment set name.
        """
        self.c.execute("""SELECT s.experiment_set_id
                          FROM experiment_set AS s
                          WHERE s.name = ?""", (set_name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_regulator_id(self, name):
        """Gets the regulator id matching the given regulator name.

        Returns: id
        """
        self.c.execute("""SELECT reg.regulator_id
                          FROM regulators AS reg
                          WHERE reg.regulator_name = ?""", (name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_id(self, name, reg_id):
        """Gets the experiment id matching the given experiment name and regulator id.
        If reg_id is None, experiment is returned if the name matches and if
        the loop_variable of the experiment is 1 and the regulator of the experiment
        is NULL.

        Returns: id
        """
        if reg_id:
            self.c.execute('SELECT e.experiment_id FROM experiment_annotation AS e WHERE e.name = ? AND e.regulator_id = ?', (name, reg_id))
        else:
            self.c.execute('SELECT e.experiment_id FROM experiment_annotation AS e WHERE e.name = ? AND e.regulator_id IS NULL AND e.loop_variable = 1', (name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_ids(self, reg_id):
        """Gets all experiment ids matching the given regulator id.

        Returns: [experiment id]
        """
        self.c.execute('SELECT e.experiment_id FROM experiment_annotation AS e WHERE e.regulator_id = ?', (reg_id,))
        return [id for (id,) in self.c.fetchall()]

    def get_experiment_dataset_id(self, experiment_id):
        """Gets the dataset id for the given experiment.

        Returns: id
        """
        self.c.execute("""SELECT e.dataset_id
                          FROM experiment_annotation AS e
                          WHERE e.experiment_id = ?""", (experiment_id,))
        return self.c.fetchone()[0]

    def get_regulators(self):
        """Gets all regulator names.

        Returns: [regulator name]
        """
        self.c.execute('SELECT regulators.regulator_name FROM regulators')
        return [reg for (reg,) in self.c.fetchall()]

    def get_target_sets(self):
        """Gets all target sets.

        Returns a mapping from experiment_id to target gene ids.
        For example:
        {1: [494], 2: [123, 456]}
        """
        self.c.execute("""SELECT t.experiment_id, t.gene_id
                          FROM target_sets AS t""")
        d = {}
        for (exp_id, gene_id) in self.c.fetchall():
            d[exp_id] = gene_id
        return d

    def get_supplementary_annotations(self):
        """Gets all supplementary annotations.

        Returns: [(dataset type, dataset name, description)]
        """
        self.c.execute('SELECT DISTINCT s.supp_dataset_type, s.supp_dataset_name, s.description FROM supplementary_dataset_annotation AS s')
        return self.c.fetchall()

    def get_supplementary_annotation_ids(self, reg_id):
        """Gets supplementary annotation names and ids that have either the
        given regulator or no regulator at all.

        Returns: [dataset name, dataset id]
        """
        self.c.execute("""SELECT s.supp_dataset_name, s.supp_dataset_id
                          FROM supplementary_dataset_annotation AS s
                          WHERE (s.regulator_id IS NULL OR s.regulator_id = ?)""", (reg_id,))
        return self.c.fetchall()

    def get_experiment_names(self):
        """Gets all experiment names.

        Returns: [experiment name]
        """
        self.c.execute('SELECT DISTINCT e.name FROM experiment_annotation AS e')
        return [name for (name,) in self.c.fetchall()]

    def get_z_scores(self, gene_ids, dataset_id):
        """Gets z-scores for the given genes in the given dataset.

        Returns: [gene id, zscore]
        """
        args = [dataset_id] + gene_ids
        self.c.execute("""SELECT z.gene_id, z.mean_z_score
                          FROM z_scores AS z
                          WHERE z.dataset_id = ?
                            AND z.gene_id IN (%s)""" % self.__to_placeholders(gene_ids), args)
        return self.c.fetchall()

    def get_gene_ids_by_name_in_experiments(self, experiment_ids, names):
        """Gets all gene ids that have results in the given experiments and that
        have matching aliases or probe_names.
        """
        query = """SELECT DISTINCT ga.gene_id
                   FROM gene_aliases AS ga, results AS r
                   WHERE ga.alias IN (%s)
                   AND ga.gene_id = r.gene_id
                   AND r.experiment_id IN (%s)
                   UNION
                   SELECT DISTINCT g.gene_id
                   FROM genes AS g, results AS r
                   WHERE g.probe_name IN (%s)
                   AND g.gene_id = r.gene_id
                   AND r.experiment_id IN (%s)""" % (self.__to_placeholders(names), self.__to_placeholders(experiment_ids), self.__to_placeholders(names), self.__to_placeholders(experiment_ids))
        args = names + experiment_ids + names + experiment_ids
        self.c.execute(query, args)
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def get_gene_aliases(self, gene_ids):
        """Gets all aliases for the given gene ids.

        Returns: [gene id, alias class, alias]
        """
        self.c.execute("""SELECT ga.gene_id, aa.alias_class, ga.alias
                          FROM gene_aliases AS ga, alias_annotation AS aa
                          WHERE ga.alias_id = aa.alias_id
                            AND gene_id IN (%s)""" % self.__to_placeholders(gene_ids), gene_ids)
        return self.c.fetchall()

    def get_alias_annotations(self, dataset_id):
        """Gets all alias annotations for the given dataset.

        Returns: [alias id, alias class, source, description]
        """
        self.c.execute("""SELECT aa.alias_id, aa.alias_class, aa.source, aa.description
                          FROM alias_annotation AS aa
                          WHERE aa.dataset_id = ?""", (dataset_id,))
        return self.c.fetchall()

    def get_dataset_figure_filename(self, dataset_id):
        """Gets the figure filename for the given dataset.

        Returns: figure_filename
        """
        self.c.execute("""SELECT d.figure_filename
                          FROM expression_dataset_annotation AS d
                          WHERE d.dataset_id = ?""", (dataset_id,))
        filename = self.c.fetchone()
        if filename:
            return filename[0]

    def get_experiment_figures(self, experiment_ids):
        """Gets all unique figure annotations for the given experiment ids.

        Returns: [(figure id, filename, name, description, priority)]
        """
        self.c.execute("""SELECT DISTINCT fa.figure_id, fa.filename, fa.name, fa.description, fa.priority
                          FROM figures AS f, figure_annotation AS fa
                          WHERE f.figure_id = fa.figure_id
                            AND f.experiment_id IN (%s)
                            ORDER BY fa.priority DESC""" % self.__to_placeholders(experiment_ids), tuple(experiment_ids))
        return self.c.fetchall()

    def get_figure_annotations(self):
        """Gets all figure annotations.

        Returns: [(figure_id, filename, name, description, priority)]
        """
        self.c.execute("""SELECT f.figure_id, f.filename, f.name, f.description, f.priority
                          FROM figure_annotation AS f""")
        return self.c.fetchall()

    def get_figure_experiments(self, figure_id):
        """Gets all experiment ids which have the given figure.
        """
        self.c.execute("""SELECT f.experiment_id
                          FROM figures AS f
                          WHERE f.figure_id = ?""", (figure_id,))
        return [experiment_id for (experiment_id,) in self.c.fetchall()]

    def get_experiment_name(self, experiment_id):
        """Gets experiment name.

        Returns: experiment_name
        """
        self.c.execute("""SELECT e.name
                          FROM experiment_annotation AS e
                          WHERE e.experiment_id = ?""", (experiment_id,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_regulator_name(self, experiment_id):
        """Gets the regulator in the experiment.

        Returns: regulator_name
        """
        self.c.execute("""SELECT r.regulator_name
                          FROM regulators AS r, experiment_annotation AS e
                          WHERE e.regulator_id = r.regulator_id
                            AND e.experiment_id = ?""", (experiment_id,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_target_genes(self, experiment_id):
        """Gets target gene names of the given experiment.

        Returns: [probe_name]
        """
        self.c.execute("""SELECT g.probe_name
                          FROM genes AS g, target_sets AS t
                          WHERE t.experiment_id = ?
                            AND g.gene_id = t.gene_id""", (experiment_id,))
        return [probe_name for (probe_name,) in self.c.fetchall()]

    def get_experiment_dataset_name(self, experiment_id):
        """Gets the dataset name of the given experiment.

        Returns: dataset_name
        """
        self.c.execute("""SELECT d.dataset_name
                          FROM expression_dataset_annotation AS d, experiment_annotation AS e
                          WHERE d.dataset_id = e.dataset_id""")
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_dataset_annotations(self):
        """Gets all dataset annotations.

        Returns: [(dataset_id, dataset_name, species, source, platform, desc, save_location, figure_filename)]
        """
        self.c.execute("""SELECT d.dataset_id, d.dataset_name, d.species, d.source, d.platform, d.description, d.save_location, d.figure_filename
                          FROM expression_dataset_annotation AS d""")
        return self.c.fetchall()

    def get_gene_supplementary_datas(self, gene_ids, supp_ids):
        """Gets the given supplementary data for the given gene ids.

        Returns: [gene id, dataset name, value]
        """
        self.c.execute("""SELECT supp.gene_id, supp_a.supp_dataset_name, supp.value
                          FROM supplementary_data AS supp, supplementary_dataset_annotation AS supp_a
                          WHERE supp.supp_dataset_id = supp_a.supp_dataset_id
                            AND supp.gene_id IN (%s)
                            AND supp_a.supp_dataset_id IN (%s)""" % (self.__to_placeholders(gene_ids), self.__to_placeholders(supp_ids)), gene_ids + list(supp_ids.values()))

        return self.c.fetchall()

    def create_filter_query(self, reg_id, filters, supp_options, supp_ids):
        """Creates a filter query.

        Parameters:

        filters = dictionary of the given form: {entity: [(symbol, value)]}
        The entity can be either an experiment name or 'zscore'. The experiment
        name can have '_baseline' or '_diff' appended to it in which case
        the filter is done by baseline_log_likelihood or by
        log_likelihood - baseline_log_likelihood correspondingly.
        Symbol can be one of the following: '>', '>=', '=', '<=', '<'.
        Value must be a number.

        Example:
        filters = {'GPSIM_diff': [('>', 0.0)], 'zscore': [('=', 0.0)], 'GPDISIM': [('>', 4.0), ('<', 500.0)]}

        supp_options = list of the following form: [(supplementary dataset name, symbol, value)]
        Symbol can be one of the following: '>', '>=', '=', '<=', '<'.
        Value must be a number.

        Example:
        supp_options = [(u'ischip', '=', '1.0'), (u'hasinsitu', '=', '0.0'), (u'chipdist', '>', '3')]

        supp_ids = dictionary of supplementary dataset names to their ids.
        NOTE: The regulator in the supplementary dataset must match reg_id or be NULL.

        Example:
        supp_ids = {u'ischip': 4, u'chipdist': 19, u'isinsitu': 3, u'hasinsitu': 2}


        Returns: (query string, query arguments)

        The query string is used to find all gene ids that match the given filters.
        """
        if not filters:
            return self.__create_supplementary_data_queries(supp_options, supp_ids)

        query = []
        args = []
        for (name, criteria) in list(filters.items()):
            parts = name.split('_')
            filterby = parts[0]
            baseline = False
            diff = False
            if len(parts) > 1:
                filterby = '_'.join(parts[:-1])
                if parts[-1] == 'baseline':
                    baseline = True
                elif parts[-1] == 'diff':
                    diff = True
                else:
                    filterby = name
            experiment_id = self.get_experiment_id(filterby, reg_id)
            q, a = self.__create_filter(filterby, criteria, experiment_id, baseline, diff)
            query.append(q)
            args += a

        supp_query, supp_args = self.__create_supplementary_data_queries(supp_options, supp_ids)

        if supp_query != '':
            query.append(supp_query)
            args += supp_args

        query = '\nINTERSECT\n'.join(query)
        return query, args

    def create_sort_query(self, filter_query, filter_args, experiment_id, sort_by_diff, sort_by_zscore):
        """Creates a sort query.

        Parameters:

        filter_query = filter query from return value of create_filter_query()
        filter_args = filter query arguments from return value of create_filter_query()
        experiment_id = the genes in the query result are sorted by the
        log_likelihood of the given experiment id


        Returns: (query string, query arguments)

        The query string is used to find all filtered genes sorted by
        the log_likelihood of the given experiment result.
        """
        fq = ''
        fa = []
        if filter_query != '':
            fq = """ AND r.gene_id IN (%s)""" % filter_query
            fa = filter_args

        if sort_by_zscore:
            query = """SELECT r.gene_id
                       FROM results AS r, z_scores AS z
                       WHERE r.gene_id = z.gene_id
                         AND r.experiment_id = ? """ + fq + " ORDER BY z.mean_z_score DESC"
        else:
            if sort_by_diff:
                order_by = " ORDER BY (r.log_likelihood - r.baseline_log_likelihood)"
            else:
                order_by = " ORDER BY r.log_likelihood"

            query = """SELECT r.gene_id
                       FROM results AS r
                       WHERE r.experiment_id = ? """ + fq + order_by + " DESC"

        args = [experiment_id] + fa
        return query, args

    def get_gene_ids_for_results(self, sort_query, sort_args):
        """Executes the given query with the given arguments.
        The query and arguments are return values of create_sort_query()

        Returns: [gene id]
        """
        self.c.execute(sort_query, tuple(sort_args))
        return [id for (id,) in self.c.fetchall()]

    def get_results_for_gene_ids(self, experiment_ids, gene_ids):
        """Gets results of the given experiments for the given genes.

        Returns: [(probe name, experiment description, log likelihood, baseline log likelihood, gene id, params, experiment_id)]
        """
        query = """SELECT g.probe_name, e.description, r.log_likelihood, r.baseline_log_likelihood, r.gene_id, r.params, e.experiment_id
                   FROM genes AS g, results AS r, experiment_annotation AS e
                   WHERE g.gene_id = r.gene_id
                     AND r.experiment_id = e.experiment_id
                     AND r.experiment_id IN (%s)
                     AND g.gene_id IN (%s)""" % (self.__to_placeholders(experiment_ids), self.__to_placeholders(gene_ids))
        args = experiment_ids + gene_ids
        self.c.execute(query, tuple(args))
        return self.c.fetchall()

    def get_gene_probe_names_dict(self, gene_ids):
        """Returns a dictionary mappings from gene id to gene probe name.

        Example: {8194: u'FBgn0028420', 6150: u'FBgn0035308', 2577: u'FBgn0011828', 18: u'FBgn0010434'}
        """
        d = {}
        self.c.execute("""SELECT g.gene_id, g.probe_name
                          FROM genes AS g
                          WHERE g.gene_id IN (%s)""" % self.__to_placeholders(gene_ids), gene_ids)
        for (id, name) in self.c.fetchall():
            d[id] = name
        return d

    def get_gene_ids_dict(self, probe_names):
        """Returns a dictionary mapping from gene id to gene probe name.

        Example: {u'FBgn0028420': 8194, u'FBgn0035308': 6150, u'FBgn0011828': 2577, u'FBgn0010434': 18}
        """
        d = {}
        self.c.execute("""SELECT g.gene_id, g.probe_name
                          FROM genes AS g
                          WHERE g.probe_name IN (%s)""" % self.__to_placeholders(probe_names), probe_names)
        for (id, name) in self.c.fetchall():
            d[name] = id
        return d

    def get_highlights(self, supp_options, supp_ids, gene_ids):
        """Gets highlighted gene ids for the given supplementary options.

        Returns a dictionary mapping from supplementary dataset name to a list of gene ids
        Example:
        {u'ischip': [3341], u'chipdist': [3341, 8354], u'hasinsitu': [3341]}
        """
        if not gene_ids:
            return {}
        highlights = {}
        for (name, symbol, value) in supp_options:
            q, a = self.__create_supplementary_data_query(supp_ids[name], symbol, float(value), gene_ids)
            self.c.execute(q, a)
            highlights[name] = [id for (id,) in self.c.fetchall()]
        return highlights

    def get_experiment_parameter_count(self, experiment_id):
        """Gets the number_of_parameters field for the given experiment.
        """
        query = """SELECT e.number_of_parameters
                   FROM experiment_annotation AS e
                   WHERE e.experiment_id = ?"""
        self.c.execute(query, (experiment_id,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_parameter_names(self, experiment_id):
        """Gets the parameters_names field for the given experiment.
        """
        query = """SELECT e.parameter_names
                   FROM experiment_annotation AS e
                   WHERE e.experiment_id = ?"""
        self.c.execute(query, (experiment_id,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_experiment_ids_names(self, experiment_ids):
        """Returns a list of experiment_ids and the corresponding names.
        Example:
            [(1, "GPSIM"), (2, "GPDISIM"), (3, "GPSIM"), (4, "GPDISIM"), (5, "MarLL")]
        """
        query = """SELECT e.experiment_id, e.name
                   FROM experiment_annotation AS e
                   WHERE e.experiment_id IN (%s)""" % self.__to_placeholders(experiment_ids)
        self.c.execute(query, experiment_ids)
        return self.c.fetchall()

    def get_figuredata(self, figure_id, gene_id):
        """Returns figure blob data corresponding the given arguments.

        Returns: binary blob
        """
        query = """SELECT f.data
                   FROM figuredata AS f
                   WHERE f.figure_id = ?
                     AND f.gene_id = ?"""
        self.c.execute(query, (figure_id, gene_id))
        result = self.c.fetchone()
        if result:
            return result[0]

    def get_version(self):
        """Returns the database version (user_version in SQLite).
        """
        self.c.execute("PRAGMA user_version")
        return self.c.fetchone()[0]

    def get_gene_count(self):
        """Returns the number of genes in the database.
        """
        self.c.execute("SELECT COUNT(*) FROM genes")
        return self.c.fetchone()[0]

