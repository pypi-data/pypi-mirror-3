function add_click_handler(checkbox, elem) {
	$(checkbox).click(function() {
		if ($(checkbox).is(":checked")) {
			$(elem).show()
		} else {
			$(elem).hide()
		}
	});

	if (!$(checkbox).is(":checked")) {
		$(elem).hide()
	}
}

$(document).ready(function() {
	add_click_handler("#show_parameters", ".parameter_table")
	add_click_handler("#show_genelist", "#gene_namelist")
	add_click_handler("#show_dataset_figure", ".figure_dataset")

	$("input[id^='show_experiment_figure_']").each(function() {
		var num = $(this).attr("id").split('_')[3]
		add_click_handler(this, ".figure_experiment_" + num)
	});

	$("input[id^='show_alias_annotation_']").each(function() {
		var alias_class = $(this).attr("id").split('_')[3]
		add_click_handler(this, ".alias_annotation_" + alias_class)
	});
});
