from __future__ import with_statement
import sqlite3


# TODO add documentation

class gpsim_database:
    """GPSIM database
    """

    __GPSIM_TABLES = [
            ("CREATE TABLE genes (gene_id INTEGER PRIMARY KEY, probe_name VARCHAR,"
             "CONSTRAINT genes_u UNIQUE (probe_name) ON CONFLICT IGNORE)"),

            ("CREATE TABLE gene_aliases (gene_id INTEGER, alias_id INTEGER, alias VARCHAR,"
             "CONSTRAINT gene_aliases_u UNIQUE (gene_id, alias_id, alias) ON CONFLICT IGNORE,"
             "CONSTRAINT gene_aliases_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id),"
             "CONSTRAINT gene_aliases_a_f FOREIGN KEY (alias_id) REFERENCES alias_annotation(alias_id))"),

            ("CREATE TABLE z_scores (gene_id INTEGER, dataset_id INTEGER, mean_z_score DOUBLE,"
             "CONSTRAINT z_scores_u UNIQUE (gene_id, dataset_id) ON CONFLICT IGNORE,"
             "CONSTRAINT z_scores_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id),"
             "CONSTRAINT z_scores_g_d FOREIGN KEY (dataset_id) REFERENCES expression_dataset_annotation(dataset_id))"),

            ("CREATE TABLE results (gene_id INTEGER, experiment_id INTEGER, log_likelihood DOUBLE, baseline_log_likelihood DOUBLE, params BLOB,"
             "CONSTRAINT results_u UNIQUE (gene_id, experiment_id) ON CONFLICT IGNORE,"
             "CONSTRAINT results_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id),"
             "CONSTRAINT results_e_f FOREIGN KEY (experiment_id) REFERENCES experiment_annotation(experiment_id))"),

            ("CREATE TABLE supplementary_data (gene_id INTEGER, supp_dataset_id INTEGER, value DOUBLE,"
             "CONSTRAINT supplementary_data_u UNIQUE (gene_id, supp_dataset_id) ON CONFLICT IGNORE,"
             "CONSTRAINT supplementary_data_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id),"
             "CONSTRAINT supplementary_data_s_f FOREIGN KEY (supp_dataset_id) REFERENCES supplementary_dataset_annotation(supp_dataset_id))"),

            ("CREATE TABLE target_sets (experiment_id INTEGER, gene_id INTEGER,"
             "CONSTRAINT target_sets_u UNIQUE (experiment_id, gene_id) ON CONFLICT IGNORE,"
             "CONSTRAINT target_sets_e_f FOREIGN KEY (experiment_id) REFERENCES experiment_annotation(experiment_id),"
             "CONSTRAINT target_sets_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id))"),

            ("CREATE TABLE figures (experiment_id INTEGER, figure_id INTEGER,"
             "CONSTRAINT figures_u UNIQUE (experiment_id, figure_id) ON CONFLICT IGNORE,"
             "CONSTRAINT figures_e_f FOREIGN KEY (experiment_id) REFERENCES experiment_annotation(experiment_id),"
             "CONSTRAINT figures_f_f FOREIGN KEY (figure_id) REFERENCES figure_annotation(figure_id))"),

            ("CREATE TABLE figuredata (figure_id INTEGER, gene_id INTEGER, data BLOB,"
             "CONSTRAINT figuredata_u UNIQUE (figure_id, gene_id) ON CONFLICT IGNORE,"
             "CONSTRAINT figuredata_f_f FOREIGN KEY (figure_id) REFERENCES figure_annotation(figure_id),"
             "CONSTRAINT figures_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id))"),

            ("CREATE TABLE regulators (regulator_id INTEGER PRIMARY KEY, gene_id INTEGER, dataset_id INTEGER, regulator_name VARCHAR,"
             "CONSTRAINT regulators_u UNIQUE (dataset_id, regulator_name) ON CONFLICT IGNORE,"
             "CONSTRAINT regulators_g_f FOREIGN KEY (gene_id) REFERENCES genes(gene_id),"
             "CONSTRAINT regulators_d_f FOREIGN KEY (dataset_id) REFERENCES expression_dataset_annotation(dataset_id))"),

            ("CREATE TABLE figure_annotation (figure_id INTEGER PRIMARY KEY, filename, name VARCHAR, description VARCHAR, priority INTEGER,"
             "CONSTRAINT figure_annotation_u UNIQUE (filename, name))"),

            ("CREATE TABLE experiment_annotation (experiment_id INTEGER PRIMARY KEY, dataset_id INTEGER, regulator_id INTEGER, loop_variable INTEGER, model_translation BOOLEAN, number_of_parameters INTEGER, parameter_names VARCHAR, producer VARCHAR, timestamp VARCHAR, description VARCHAR, name VARCHAR,"
             "CONSTRAINT experiment_annotation_u UNIQUE (dataset_id, regulator_id, loop_variable, model_translation, name) ON CONFLICT IGNORE,"
             "CONSTRAINT experiment_annotation_d_f FOREIGN KEY (dataset_id) REFERENCES expression_dataset_annotation(dataset_id),"
             "CONSTRAINT experiment_annotation_r_f FOREIGN KEY (regulator_id) REFERENCES regulators(regulator_id))"),

            ("CREATE TABLE experiment_set (experiment_set_id INTEGER PRIMARY KEY, parent_id INTEGER, name VARCHAR,"
             "CONSTRAINT experiment_set_u UNIQUE (name) ON CONFLICT IGNORE,"
             "CONSTRAINT experiment_set_p_f FOREIGN KEY (parent_id) REFERENCES experiment_set(experiment_set_id))"),

            ("CREATE TABLE experiment_set_experiments (experiment_set_id INTEGER, experiment_id INTEGER,"
             "CONSTRAINT experiment_set_experiments_u UNIQUE (experiment_set_id, experiment_id) ON CONFLICT IGNORE,"
             "CONSTRAINT experiment_set_experiments_s_f FOREIGN KEY (experiment_set_id) REFERENCES experiment_set(experiment_set_id),"
             "CONSTRAINT experiment_set_experiments_e_f FOREIGN KEY (experiment_id) REFERENCES experiment_annotation(experiment_id))"),

            ("CREATE TABLE expression_dataset_annotation (dataset_id INTEGER PRIMARY KEY, dataset_name VARCHAR, species VARCHAR, source VARCHAR, platform VARCHAR, description VARCHAR, save_location VARCHAR, figure_filename VARCHAR,"
             "CONSTRAINT expression_dataset_annotation_u UNIQUE (dataset_name) ON CONFLICT IGNORE)"),

            ("CREATE TABLE alias_annotation (alias_id INTEGER PRIMARY KEY, dataset_id INTEGER, alias_class VARCHAR, source VARCHAR, description VARCHAR,"
             "CONSTRAINT alias_annotation_u UNIQUE (dataset_id, alias_class) ON CONFLICT IGNORE,"
             "CONSTRAINT alias_annotation_d_f FOREIGN KEY (dataset_id) REFERENCES expression_dataset_annotation(dataset_id))"),

            ("CREATE TABLE supplementary_dataset_annotation (supp_dataset_id INTEGER PRIMARY KEY, supp_dataset_type INTEGER, supp_dataset_name VARCHAR, regulator_id INTEGER, source VARCHAR, platform VARCHAR, description VARCHAR,"
             "CONSTRAINT supplementary_dataset_annotation_u UNIQUE (supp_dataset_name, regulator_id) ON CONFLICT IGNORE,"
             "CONSTRAINT supplementary_dataset_annotation_r_f FOREIGN KEY (regulator_id) REFERENCES regulators(regulator_id))")]

    __VERSION = 1 #: Database schema version

    def __init__(self, sqlite_file):
        """Connects to a given database file.
        Creates a new file and database if it doesn't exist.
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

    def __filter_nones(self, values):
        return [x for x in values if x != None]

    def __insert_table_values(self, table, values):
        self.c.execute('INSERT INTO %s VALUES (%s)'
                % (table, self.__to_placeholders(values)), self.__filter_nones(values))
        return self.c.lastrowid

    def __add_gene_aliases(self, gene_id=0, alias_id=0, alias=""):
        self.__insert_table_values("gene_aliases", (gene_id, alias_id, alias))

    def __add_z_scores(self, gene_id=0, dataset_id=0, mean_z_score=0.0):
        self.__insert_table_values("z_scores", (gene_id, dataset_id, mean_z_score))

    def __add_results(self, gene_dataset_id=0, experiment_id=0, log_likelihood=0.0, baseline_log_likelihood=None, params=None):
        self.__insert_table_values("results", (gene_dataset_id, experiment_id, log_likelihood, baseline_log_likelihood, params))

    def __add_target_sets(self, experiment_id=0, gene_id=0):
        self.__insert_table_values("target_sets", (experiment_id, gene_id))

    def __add_supplementary_data(self, gene_id=0, supp_dataset_id=0, value=0.0):
        self.__insert_table_values("supplementary_data", (gene_id, supp_dataset_id, value))

    def __add_figures(self, experiment_id=0, figure_id=0):
        self.__insert_table_values("figures", (experiment_id, figure_id))

    def __add_experiment_set_experiments(self, experiment_set_id=0, experiment_id=0):
        self.__insert_table_values("experiment_set_experiments", (experiment_set_id, experiment_id))

    def __add_experiment_set(self, parent_id=None, name=""):
        return self.__insert_table_values("experiment_set", (None, parent_id, name))

    def __add_regulators(self, gene_id=None, dataset_id=None, regulator_name=""):
        return self.__insert_table_values("regulators", (None, gene_id, dataset_id, regulator_name))

    def __add_genes(self, probe_name=""):
        return self.__insert_table_values("genes", (None, probe_name))

    def __add_figure_annotation(self, filename="", name="", description="", priority=0):
        return self.__insert_table_values("figure_annotation", (None, filename, name, description, priority))

    def __add_experiment_annotation(self, dataset_id=0, regulator_id=0,
            loop_variable=1, model_translation=False, number_of_parameters=0,
            parameter_names="", producer="", timestamp="", description="", name=""):
        return self.__insert_table_values("experiment_annotation",
                (None, dataset_id, regulator_id, loop_variable, model_translation,
                 number_of_parameters, parameter_names, producer, timestamp, description, name))

    def __add_expression_dataset_annotation(self, dataset_name="", species="",
            source="", platform="", description="", save_location="", figure_filename=""):
        return self.__insert_table_values("expression_dataset_annotation",
                (None, dataset_name, species, source, platform, description, save_location, figure_filename))

    def __add_alias_annotation(self, dataset_id=0, alias_class="", source="", description=""):
        return self.__insert_table_values("alias_annotation",
                (None, dataset_id, alias_class, source, description))

    def __add_supplementary_dataset_annotation(self, supp_dataset_type=0,
            supp_dataset_name="", regulator_id=None, source="", platform="", description=""):
        return self.__insert_table_values("supplementary_dataset_annotation",
                (None, supp_dataset_type, supp_dataset_name, regulator_id, source, platform, description))

    def __get_genes(self):
        self.c.execute("""SELECT g.probe_name, g.gene_id FROM genes AS g""")
        return self.c.fetchall()

    def __get_regulator_gene(self, regulator_name):
        self.c.execute("""SELECT ga.gene_id, a.dataset_id
                          FROM gene_aliases AS ga, alias_annotation AS a
                          WHERE ga.alias = ?
                            AND ga.alias_id = a.alias_id""", (regulator_name,))
        result = self.c.fetchone()
        if result:
            return result
        return None, None

    def __get_supplementary_annotation_id(self, name, regulator_id):
        if regulator_id:
            q = """SELECT s.supp_dataset_id
                   FROM supplementary_dataset_annotation AS s
                   WHERE s.supp_dataset_name = ?
                     AND s.regulator_id = ?"""
            a = (name, regulator_id)
        else:
            q = """SELECT s.supp_dataset_id
                   FROM supplementary_dataset_annotation AS s
                   WHERE s.supp_dataset_name = ?"""
            a = (name,)
        self.c.execute(q, a)
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_experiment_annotation_id(self, dataset_id, reg_id, name):
        self.c.execute("""SELECT e.experiment_id
                          FROM experiment_annotation AS e
                          WHERE e.dataset_id = ?
                            AND (e.regulator_id = ?
                              OR (e.regulator_id IS NULL AND e.loop_variable = 1))
                            AND e.name = ?""", (dataset_id, reg_id, name))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_figure_annotation_id(self, filename):
        self.c.execute("""SELECT f.figure_id
                          FROM figure_annotation AS f
                          WHERE f.filename = ?""", (filename,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_regulator_id(self, regulator_name):
        self.c.execute("""SELECT r.regulator_id
                          FROM regulators AS r
                          WHERE r.regulator_name = ?""", (regulator_name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_experiment_set_id(self, name):
        self.c.execute("""SELECT s.experiment_set_id
                          FROM experiment_set AS s
                          WHERE s.name = ?""", (name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_expression_dataset_annotation_id(self, name):
        self.c.execute("""SELECT e.dataset_id
                          FROM expression_dataset_annotation AS e
                          WHERE e.dataset_name = ?""", (name,))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_alias_annotation_id(self, dataset_id, alias_class, source, desc):
        self.c.execute("""SELECT a.alias_id
                          FROM alias_annotation AS a
                          WHERE a.dataset_id = ?
                            AND a.alias_class = ?""", (dataset_id, alias_class))
        result = self.c.fetchone()
        if result:
            return result[0]

    def __get_genes_with_supplementary_data(self, supp_dataset_id):
        self.c.execute("""SELECT s.gene_id
                          FROM supplementary_data AS s
                          WHERE s.supp_dataset_id = ?""", (supp_dataset_id,))
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def __get_genes_with_zscore(self, dataset_id):
        self.c.execute("""SELECT z.gene_id
                          FROM z_scores AS z
                          WHERE z.dataset_id = ?""", (dataset_id,))
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def __get_genes_with_result(self, experiment_id):
        self.c.execute("""SELECT r.gene_id
                          FROM results AS r
                          WHERE r.experiment_id = ?""", (experiment_id,))
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def __get_genes_with_aliases(self, alias_id):
        self.c.execute("""SELECT a.gene_id
                          FROM gene_aliases AS a
                          WHERE a.alias_id = ?""", (alias_id,))
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def __get_genes_with_experiment_target(self, experiment_id):
        self.c.execute("""SELECT t.gene_id
                          FROM target_sets AS t
                          WHERE t.experiment_id = ?""", (experiment_id,))
        return [gene_id for (gene_id,) in self.c.fetchall()]

    def __get_experiments_in_set(self, set_id):
        self.c.execute("""SELECT s.experiment_id
                          FROM experiment_set_experiments AS s
                          WHERE s.experiment_set_id = ?""", (set_id,))
        return [exp_id for (exp_id,) in self.c.fetchall()]

    def __get_experiment_figures(self, experiment_id):
        self.c.execute("""SELECT f.filename
                          FROM figure_annotation AS f, figures AS fi
                          WHERE fi.experiment_id = ?
                            AND fi.figure_id = f.figure_id""", (experiment_id,))
        return [filename for (filename,) in self.c.fetchall()]


    def create_tables(self):
        """Tries to create tables for the database.
        Throws an exception if a table cannot be created.
        """
        for l in self.__GPSIM_TABLES:
            self.c.execute(l)
        self.conn.commit()
        self.c.execute('PRAGMA user_version = ' + str(self.__VERSION))
        self.c.execute('CREATE INDEX results_index ON results (gene_id)')

    def get_version(self):
        """Gets the database schema version.
        """
        self.c.execute('PRAGMA user_version')
        return self.c.fetchone()[0]

    def dump_to_file(self, filename):
        """Dumps the SQL command log of this database connection.
        """
        self.conn.commit()
        with open(filename, 'w') as f:
            for line in self.conn.iterdump():
                f.write('%s\n' % line)

    def add_and_get_regulator_id(self, regulator_name):
        """Gets the regulator id.
        Adds the regulator to the database if necessary.
        """
        if not regulator_name:
            return None
        reg_id = self.__get_regulator_id(regulator_name)
        if not reg_id:
            gene_id, dataset_id = self.__get_regulator_gene(regulator_name)
            reg_id = self.__add_regulators(gene_id, dataset_id, regulator_name)
        return reg_id

    def add_and_get_genes_dict(self, probe_names):
        """Gets a dictionary of gene probe names and ids.
        For example: {'FBgn0000008': 1,'FBgn0000011': 2,'FBgn0000014': 3}
        Adds missing genes to the database.
        """
        names = []
        ids = []
        genes = self.__get_genes()
        if genes:
            names, ids = list(zip(*genes))
        missing = set(probe_names) - set(names)
        for name in missing:
            genes.append((name, self.__add_genes(name)))
        dict = {}
        for (name, id) in genes:
            dict[name] = id
        return dict

    def add_and_get_experiment_set(self, set_name, parent_name):
        """Gets the experiment set id.
        Adds a new experiment set if necessary.
        """
        if not set_name:
            return None
        exp_set_id = self.__get_experiment_set_id(set_name)
        if not exp_set_id:
            exp_set_id = self.__add_experiment_set(self.add_and_get_experiment_set(parent_name, None), set_name)
        return exp_set_id

    def add_and_get_supplementary_annotation(self, type, name, regulator_name, source, platform, desc):
        """Gets the supplementary annotation id.
        Adds the annotation to the database if necessary.
        Adds the regulator to the database if necessary.
        """
        reg_id = self.add_and_get_regulator_id(regulator_name)
        supp_id = self.__get_supplementary_annotation_id(name, reg_id)
        if not supp_id:
            supp_id = self.__add_supplementary_dataset_annotation(type, name, reg_id, source, platform, desc)
        return supp_id

    def add_and_get_dataset_annotation(self, name, species, source, platform, desc, save_location, figure_filename):
        """Gets the dataset annotation id.
        Adds the annotation to the database if necessary.
        """
        dataset_id = self.__get_expression_dataset_annotation_id(name)
        if not dataset_id:
            dataset_id = self.__add_expression_dataset_annotation(name, species, source, platform, desc, save_location, figure_filename)
        return dataset_id

    def add_and_get_experiment_annotation(self, dataset_id, regulator_name, loop_variable, model_translation, number_of_params, param_names, producer, timestamp, desc, name):
        """Gets the experiment annotation id.
        Adds the annotation to the database if necessary.
        Adds the regulator to the database if necessary.
        """
        reg_id = self.add_and_get_regulator_id(regulator_name)
        exp_id = self.__get_experiment_annotation_id(dataset_id, reg_id, name)
        if not exp_id:
            exp_id = self.__add_experiment_annotation(dataset_id, reg_id, loop_variable, model_translation, number_of_params, param_names, producer, timestamp, desc, name)
        return exp_id

    def add_and_get_alias_annotation(self, dataset_id, alias_class, source, description):
        """Gets the alias annotation id.
        Adds the annotation to the database if necessary.
        """
        alias_id = self.__get_alias_annotation_id(dataset_id, alias_class, source, description)
        if not alias_id:
            alias_id = self.__add_alias_annotation(dataset_id, alias_class, source, description)
        return alias_id

    def add_and_get_figure_annotation(self, filename, name, description, priority):
        """Gets the figure annotation id.
        Adds the annotation to the database if necessary.
        """
        figure_id = self.__get_figure_annotation_id(filename)
        if not figure_id:
            figure_id = self.__add_figure_annotation(filename, name, description, priority)
        return figure_id
     
    def add_supplementary_data(self, probe_names, values, supp_annotation):
        """Adds the given supplementary data to the given probe_names.
        Adds missing genes to the database.
        Adds the supplementary annotation if it doesn't exist.
        Adds the regulator if necessary.

        supp_annotation = [type, name, regulator_name, source, platform, description]
        """
        genes_dict = self.add_and_get_genes_dict(probe_names)
        gene_ids = list(genes_dict.values())
        supp_id = self.add_and_get_supplementary_annotation(*supp_annotation)
        missing = set(gene_ids) - set(self.__get_genes_with_supplementary_data(supp_id))
        for (probe_name, value) in zip(probe_names, values):
            gene_id = genes_dict[probe_name]
            if gene_id in missing:
                self.__add_supplementary_data(gene_id, supp_id, value)

    def add_zscores(self, probe_names, zscores, dataset_annotation):
        """Adds zscores to the given genes.
        Adds missing genes to the database.
        Adds dataset_annotation if it doesn't exist yet.

        dataset_annotation = [name, species, source, platform, description, save_locatio, figure_filename]
        """
        genes_dict = self.add_and_get_genes_dict(probe_names)
        gene_ids = list(genes_dict.values())
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        missing = set(gene_ids) - set(self.__get_genes_with_zscore(dataset_id))
        for (probe_name, value) in zip(probe_names, zscores):
            gene_id = genes_dict[probe_name]
            if gene_id in missing:
                self.__add_z_scores(gene_id, dataset_id, value)

    def add_experiment_results(self, probe_names, log_likelihoods, baseline_log_likelihoods, params, experiment_annotation, dataset_annotation):
        """Adds experiment results to the given genes.
        Adds missing genes to the database.
        Adds the experiment anntation if it doesn't exist.
        Adds dataset annotation if necessary.

        experiment_annotation = [regulator_name, loop_variable, model_translation, number_of_params, param_names, producer, timestamp, desc, name]
        dataset_annotation = [name, species, source, platform, description, save_locatio, figure_filename]
        """
        genes_dict = self.add_and_get_genes_dict(probe_names)
        gene_ids = list(genes_dict.values())
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        experiment_id = self.add_and_get_experiment_annotation(*([dataset_id] + experiment_annotation))
        missing = set(gene_ids) - set(self.__get_genes_with_result(experiment_id))
        for (probe_name, log_likelihood, baseline_log_likelihood, param) in zip(probe_names, log_likelihoods, baseline_log_likelihoods, params):
            gene_id = genes_dict[probe_name]
            if gene_id in missing:
                self.__add_results(gene_id, experiment_id, log_likelihood, baseline_log_likelihood, param)

    def add_experiment_set(self, set_name, parent_name, experiment_annotations, dataset_annotations):
        """Adds the given experiment to the given experiment set.
        Adds missing experiment sets (set and its parent) if necessary.
        Adds missing experiment annotations if necessary.
        Adds missing dataseset annotations if necessary.

        experiment_annotations = [[regulator_name, loop_variable, model_translation, number_of_params, param_names, producer, timestamp, desc, name]]
        dataset_annotations = [[name, species, source, platform, description, save_locatio, figure_filename]]
        """
        set_id = self.add_and_get_experiment_set(set_name, parent_name)
        exp_ids = []
        for (exp_ann, data_ann) in zip(experiment_annotations, dataset_annotations):
            dataset_id = self.add_and_get_dataset_annotation(*data_ann)
            exp_ids.append(self.add_and_get_experiment_annotation(*([dataset_id] + exp_ann)))
        missing = set(exp_ids) - set(self.__get_experiments_in_set(set_id))
        for exp_id in missing:
            self.__add_experiment_set_experiments(set_id, exp_id)

    def add_figure(self, experiment_annotation, dataset_annotation, figure_annotation):
        """Adds the given figure to the given experiment.
        Adds missing experiment annotation if necessary.
        Adds missing dataset annotation if necessary.
        Adds missing figure annotation if necessary.

        experiment_annotation = [regulator_name, loop_variable, model_translation, number_of_params, param_names, producer, timestamp, desc, name]
        dataset_annotation = [name, species, source, platform, description, save_locatio, figure_filename]
        figure_annotation = [filename, name, description, priority]
        """
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        experiment_id = self.add_and_get_experiment_annotation(*([dataset_id] + experiment_annotation))
        figure_id = self.add_and_get_figure_annotation(*figure_annotation)
        if figure_id not in self.__get_experiment_figures(experiment_id):
            self.__add_figures(experiment_id, figure_id)

    def add_target_sets(self, probe_names, experiment_annotation, dataset_annotation):
        """Adds given genes to the target set of a given experiment.
        Adds missing experiment annotation if necessary.
        Adds missing genes if necessary.
        """
        genes_dict = self.add_and_get_genes_dict(probe_names)
        gene_ids = list(genes_dict.values())
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        experiment_id = self.add_and_get_experiment_annotation(*([dataset_id] + experiment_annotation))
        missing = set(gene_ids) - set(self.__get_genes_with_experiment_target(experiment_id))
        for probe_name in probe_names:
            gene_id = genes_dict[probe_name]
            if gene_id in missing:
                self.__add_target_sets(experiment_id, gene_id)

    def add_aliases(self, probe_names, aliases, alias_annotation, dataset_annotation):
        """Adds aliases to genes.
        Adds missing genes.
        Adds missing alias annotation.
        Adds missing dataset annotation.

        dataset_annotations = [name, species, source, platform, description, save_locatio, figure_filename]
        alias_annotation = [alias_class, source, description]
        """
        genes_dict = self.add_and_get_genes_dict(probe_names)
        gene_ids = list(genes_dict.values())
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        alias_id = self.add_and_get_alias_annotation(*([dataset_id] + alias_annotation))
        missing = set(gene_ids) - set(self.__get_genes_with_aliases(alias_id))
        for (probe_name, alias) in zip(probe_names, aliases):
            gene_id = genes_dict[probe_name]
            if gene_id in missing:
                self.__add_gene_aliases(gene_id, alias_id, alias)

    def add_regulator(self, regulator_name, probe_name, dataset_annotation):
        """Adds the given regulator to the database.
        Adds dataset annotation if necessary.
        Adds a gene if probe_name is defined.
        """
        reg_id = self.__get_regulator_id(regulator_name)
        if reg_id:
            return
        gene_id = None
        if probe_name:
            genes_dict = self.add_and_get_genes_dict([probe_name])
            gene_id = genes_dict[probe_name]
        
        dataset_id = self.add_and_get_dataset_annotation(*dataset_annotation)
        self.__add_regulators(gene_id, dataset_id, regulator_name)

