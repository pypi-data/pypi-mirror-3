from tigreBrowser.database import *
import xdrlib

class Results:
    """This class is responsible for getting the results from the database
    using functions in database.py.
    """
    def __init__(self, db, experiment_set, regulator, target_set, experiment, filters, supplementary_options, search_genes):
        """Initialization. Does not, however, fetch the results.
        Parameters:
            db: database object

            experiment_set: name of the experiment set

            regulator: name of the regulator if it exists

            target_set: name of the target set if it exists

            experiment: name of the experiment, appended with '_diff'
                        if sorting is to be done by diff.
                        Can also be 'zscore' if sorting is done by z-scores

            filters: filters that will be applied when fetching
                     and filtering results (see create_filter_query() in
                     database.py for explanation about the parameter type)

            supplementary_options: highlights will be fetched according
                                   to these options (see create_filter_query()
                                   in database.py for explanation about
                                   the parameter type)

            search_genes: search these gene names or aliases (list of strings)
        """
        self.__db = db
        self.__set_id = db.get_experiment_set_id(experiment_set)
        self.__reg_id = db.get_regulator_id(regulator)
        self.__set_experiment_ids = db.get_experiment_ids_in_set_recursively(self.__set_id)

        if target_set:
            self.__target_ids = db.get_gene_ids_dict(target_set).values()
        self.__experiment_id = db.get_experiment_id(experiment.replace('_diff', ''), self.__reg_id)
        self.__sort_by_diff = experiment.endswith('_diff')
        self.__sort_by_zscore = False

        if experiment == 'zscore':
            self.__experiment_id = self.__set_experiment_ids[0]
            self.__sort_by_zscore = True

        if not self.__experiment_id:
            raise Exception('No experiment with the current TF')

        self.__dataset_id = db.get_experiment_dataset_id(self.__experiment_id)
        self.__supplementary_annotation_ids_dict = self.__create_supplementary_annotation_ids_dict(self.__reg_id)
        self.__filters = filters
        self.__supplementary_options = supplementary_options

        regulator_experiment_ids = db.get_experiment_ids(self.__reg_id)

        # If a regulator is defined (TARGET_RANKING),
        # choose only the experiments in a set that have the given regulator.
        # Use set intersection.
        if self.__reg_id:
            self.__set_experiment_ids = list(set(self.__set_experiment_ids) & set(regulator_experiment_ids))

        self.__search_gene_ids = None
        if search_genes:
            self.__search_gene_ids = db.get_gene_ids_by_name_in_experiments(self.__set_experiment_ids, search_genes)

        if not self.__set_experiment_ids:
            raise Exception('No results for the given selection')

        for (name, symbol, value) in supplementary_options:
            if name not in self.__supplementary_annotation_ids_dict:
                raise Exception('Supplementary option %s not available for the given TF' % name)

        self.__results_all = {}
        self.__aliases_all = {}
        self.__params_all = {}
        self.__supps_all = {}
        self.__zscores_all = {}
        self.__probe_names = {}
        self.__highlights = {}

    def __create_supplementary_annotation_ids_dict(self, reg_id):
        d = {}
        for (name, ann_id) in self.__db.get_supplementary_annotation_ids(reg_id):
            d[name] = ann_id
        return d

    def __parse_results(self, results):
        self.__experiment_parameter_names = self.__get_experiment_parameter_names()
        result_gene_ids = set()
        probe_names = {}
        results_all = {}
        params_all = {}
        for row in results:
            probe_name = row[0]
            desc = row[1]
            likelihood = row[2]
            baseline_likelihood = row[3]
            gene_id = row[4]
            param_values = row[5]
            exp_id = row[6]
            result_gene_ids.add(gene_id)

            results_all.setdefault(gene_id, {})[desc] = likelihood

            # add results with appended '_baseline' and '_diff'
            # if baseline is defined to show them in results listing
            if baseline_likelihood:
                results_all[gene_id][desc + '_baseline'] = baseline_likelihood
                results_all[gene_id][desc + '_diff'] = likelihood - baseline_likelihood
            probe_names[gene_id] = probe_name
            params_all.setdefault(gene_id, {})[exp_id] = self.__map_params_to_names(exp_id, self.__experiment_parameter_names.get(exp_id, []), param_values)
        return result_gene_ids, probe_names, results_all, params_all

    def __query_supplementary_datas(self, gene_ids, supp_ids):
        supps = self.__db.get_gene_supplementary_datas(gene_ids, supp_ids)
        d = {}
        for (supp_id, name, value) in supps:
            d.setdefault(supp_id, {})[name] = value
        return d

    def __query_gene_aliases(self, gene_ids):
        aliases = self.__db.get_gene_aliases(gene_ids)
        d = {}
        for (alias_id, alias_class, alias) in aliases:
            d.setdefault(alias_id, {}).setdefault(alias_class, []).append(alias)
        return d

    def __query_zscores(self, gene_ids, dataset_id):
        d = {}
        for (gene_id, zscore) in self.__db.get_z_scores(gene_ids, dataset_id):
            d[gene_id] = zscore
        return d

    def __parse_rdata_double_raw_vector(self, data_buffer):
        # Python 2.5 and 3.x compatibility code
        try:
            header = [ord(x) for x in [data_buffer[0], data_buffer[1]]]
        except TypeError:
            header = [data_buffer[0], data_buffer[1]]

        # RData binary format
        if header[0] != ord('X') or header[1] != ord('\n'):
            return None
        xdr = xdrlib.Unpacker(data_buffer[2:])
        xdr.unpack_int()
        xdr.unpack_int()
        xdr.unpack_int()
        xdr.unpack_int()
        xdr.unpack_int()
        data = []
        while True:
            try:
                data.append(xdr.unpack_double())
            except EOFError:
                break
        return data

    def __map_params_to_names(self, exp_id, param_names, param_values):
        if not param_values:
            return {}
        param_values = self.__parse_rdata_double_raw_vector(param_values)
        return dict(zip(param_names, param_values))

    def fetch_results(self, number_of_genes, offset):
        """Fetches the results from the database.

        Parameters:
            number_of_genes: fetch at most this many genes

            offset: offset in the results listing

        Returns: (gene ids for the result genes, total number of genes with results)
        """
        fq, fa = self.__db.create_filter_query(self.__reg_id, self.__filters, [], self.__supplementary_annotation_ids_dict)
        sq, sa = self.__db.create_sort_query(fq, fa, self.__experiment_id, self.__sort_by_diff, self.__sort_by_zscore)

        if self.__search_gene_ids != None:
            gene_ids = self.__search_gene_ids
        else:
            gene_ids = self.__db.get_gene_ids_for_results(sq, sa)

        count = len(gene_ids) # total result count
        gene_ids = gene_ids[offset:(offset + number_of_genes)] # OFFSET, LIMIT

        results = self.__db.get_results_for_gene_ids(self.__set_experiment_ids, gene_ids)
        result_gene_ids, self.__probe_names, self.__results_all, self.__params_all = self.__parse_results(results)

        if not results: # quick fix for the result count
            count = 0

        # remove gene ids that are in gene_ids but not in result_gene_ids
        l = gene_ids[:]
        for gene_id in l:
            if gene_id not in result_gene_ids:
                gene_ids.remove(gene_id)

        self.__supps_all = self.__query_supplementary_datas(gene_ids, self.__supplementary_annotation_ids_dict)
        self.__aliases_all = self.__query_gene_aliases(gene_ids)
        self.__zscores_all = self.__query_zscores(gene_ids, self.__dataset_id)

        self.__highlights = self.__db.get_highlights(self.__supplementary_options, self.__supplementary_annotation_ids_dict, gene_ids)

        return gene_ids, count

    def get_experiment_results(self, gene_id):
        """Returns a dictionary of experiment results for the given gene_id.

        Returns: {experiment_name, log_likelihood or baseline_log_likelihood}

        Example:
            {'GPDISIM_diff': 494.65294095332217, 'GPDISIM': 6.7597099032014309, 'GPDISIM_baseline': -487.89323105012073}
        """
        return self.__results_all.get(gene_id)

    def get_zscore(self, gene_id):
        """Returns z-score for the given gene_id.
        """
        return self.__zscores_all.get(gene_id)

    def get_supplementary_data(self, gene_id):
        """Returns a dictionary representing supplementary data
        for the given gene_id.

        Returns: {supplementary dataset name, value}

        Example:
            {'ischip': 1.0, 'chipdist': 1671.0, 'isinsitu': 0.0, 'hasinsitu': 0.0}
        """
        return self.__supps_all.get(gene_id, {})

    def get_parameters(self, gene_id):
        """Returns a dictionary of parameters in different experiments
        for the given gene id.

        Returns: {experiment id: {parameter name: parameter value}}

        Example:
            {1: {'rbf1_variance/disim1_rbf_variance': 0.59039292169555113,
                 'disim1_variance': -5.9057868788275316,
                 'disim1_decay': -3.9377851775471258,
                 'disim1_di_variance': 0.0,
                 'Basal1': -8.9106876980653453,
                 'disim1_di_decay': -4.0190835928767878,
                 'rbf1_inverseWidth/disim1_inverseWidth': -0.51096542027712455}
            }
        """
        return self.__params_all.get(gene_id, {})

    def get_aliases(self, gene_id):
        """Returns a dictionary of aliases for the given gene id.

        Returns: {alias class, [aliases]}

        Example:
            {'ENTREZID': [u'38211'],
             'SYMBOL': [u'CG12011'],
             'FLYBASE': [u'FBgn0035257'],
             'GENENAME': [u'CG12011 gene product from transcript CG12011-RA']}
        """
        return self.__aliases_all.get(gene_id, {})

    def get_probe_name(self, gene_id):
        """Returns the probe name for the given gene id.
        """
        return self.__probe_names.get(gene_id)

    def get_highlights(self):
        """Gets a dictionary of supplementary dataset names to gene ids that
        will be highlighted.

        Returns: {supplementary dataset name: [gene ids]}

        Example:
            {'ischip': [4632, 8354, 10609], 'isinsitu': [], 'hasinsitu': [4632, 8354, 10609]}
        """
        return self.__highlights

    def get_dataset_figure(self):
        """Gets the template URL to the dataset figure.

        Example:
            http://www.something.com/something/figures/${probe_name}.png
        """
        return self.__db.get_dataset_figure_filename(self.__dataset_id)

    def get_experiment_figures(self):
        """Gets experiment figure annotations.

        Returns: [(figure id, filename, name, description, priority)]
        """
        return self.__db.get_experiment_figures(self.__set_experiment_ids)

    def get_alias_annotations(self):
        """Gets all alias annotations.

        Returns: [(alias annotation id, alias class, source, description)]
        """
        return self.__db.get_alias_annotations(self.__dataset_id)

    def get_experiment_names(self):
        """Gets a dictionary mapping from experiment ids to corresponding names.

        Returns: {experiment id: experiment name}

        Example:
            {1: 'GPDISIM', 2: 'GPSIM'}
        """
        exp_dict = {}
        results = self.__db.get_experiment_ids_names(self.__set_experiment_ids)
        for (exp_id, name) in results:
            exp_dict[exp_id] = name
        return exp_dict

    def __get_experiment_parameter_names(self):
        params_dict = {}
        for exp_id in self.__set_experiment_ids:
            names = self.__db.get_experiment_parameter_names(exp_id)
            if not names:
                continue
            names = [name.strip() for name in names.strip().split(',')]
            params_dict[exp_id] = names
        return params_dict

    def get_experiment_parameter_names(self):
        """Gets a dictionary mapping from experiment ids to a list of
        parameter names.

        Returns: {experiment id: [parameter names]}

        Example:
            {1: ['rbf1_inverseWidth/disim1_inverseWidth',
                 'rbf1_variance/disim1_rbf_variance',
                 'disim1_di_decay',
                 'disim1_di_variance',
                 'disim1_decay',
                 'disim1_variance',
                 'Basal1']
            }
        """
        return self.__experiment_parameter_names

    def get_all_parameter_names(self):
        """Gets a list of parameters names in all experiments.

        Returns: [parameter names]
        """
        all_names = sum(self.__experiment_parameter_names.values(), [])
        # remove duplicates
        names = []
        [names.append(name) for name in all_names if not names.count(name)]
        return names

