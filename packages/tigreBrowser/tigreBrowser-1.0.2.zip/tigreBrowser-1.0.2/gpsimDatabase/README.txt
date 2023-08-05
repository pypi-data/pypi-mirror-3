GPSIM database
==============


insert_aliases.py
-----------------

This script is used to insert gene aliases to the database. Let's assume that
file 'aliases.txt' contains the follwing 9 lines. Each line contains a gene
name and an alias separated by whitespace.

FBgn0000003	7SLRNA
FBgn0000008	a
FBgn0000011	ab
FBgn0000014	abd-A
FBgn0000015	Abd-B
FBgn0000017	Abl
FBgn0000018	abo
FBgn0000022	ac
FBgn0000024	Ace

The aliases in this file can be inserted to the database with the following
command:

$ python insert_aliases.py -f aliases.txt database.sqlite "Symbol" "Test dataset"

The script will add aliases to the corresponding genes in the "Test dataset"
dataset. If the dataset does not exist, it will be created. Also, if a gene
name does not exist, a gene will be created.


insert_figures.py
-----------------

Figures can be inserted to the database by using insert_figures.py script. For
example, let 'figures.txt' contain the follwing two lines:

http://www.cis.hut.fi/ahonkela/dros/score_pics2/bap/bap_${probe_name}_gpsim.png, GPSIM bap, , 5
http://www.cis.hut.fi/ahonkela/dros/score_pics2/bap/bap_${probe_name}.png, GPDISIM bap, , 6

The values in this file are separated by comma and the format of a line is as follows:
filename, figure_name, figure_description, figure_priority

If we wanted to insert the figures to an experiment "GPSIM" with a regulator
"bap", we would use the following command:

$ python insert_figures.py -f figures.txt -d ',' database.sqlite "GPSIM" "bap" "Test dataset"

The '-d' option will set the delimiter used in the file which is in this case
comma (','). The script will add those figures to an experiment which name is
"GPSIM", regulator is "bap" and dataset is "Test dataset". If any of the
forementioned is missing from the database, it will be created.


insert_results.py
-----------------

Experiment results are added using this script. Assume the file 'results.txt'
contains the following 9 lines:

FBgn ischip hasinsitu isinsitu baseline gpdisim gpsim
FBgn0000008 0 0 0 -69.308261 -100.719304 19.021085
FBgn0000011 0 0 0 -622.260758 -16.649425 57.799397
FBgn0000014 1 1 1 -94.052995 -51.492857 23.269117
FBgn0000015 1 0 0 -219.278879 -24.023653 38.973297
FBgn0000017 0 0 0 -57.974217 -87.721620 -3.315447
FBgn0000018 0 0 0 -84.989078 -116.390492 6.232027
FBgn0000022 0 1 0 -75.916914 -48.959545 4.631974
FBgn0000024 0 1 0 -4.333182 -35.734065 50.582057

If these results are from GPSIM/GPDISIM experiments with "bap" as the regulator
and we wanted like to add the GPSIM results, the following command would be
used:

$ python insert_results.py -f results.txt --log-likelihood-column=7 --baseline-log-likelihood-column=5 --experiment-set="GPSIM/GPDISIM experiments" --figure-filename='http://www.cis.hut.fi/ahonkela/dros/expro_pics/${probe_name}_exp.png' database.sqlite "Test dataset" "GPSIM" "bap" 'http://www.cis.hut.fi/ahonkela/dros/score_pics2/bap/bap_${probe_name}_gpsim.png'

The correct columns are given by options '--baseline-log-likelihood-column' and
'--log-likelihood-column'. If baseline column option is omitted, the baseline
values are not added to the database. The '--experiment-set' option will add
the experiment to the given experiment set. '--figure-filename' is a filename
template for gene expression figures.

The script will add results to an experiment which name is "GPSIM", regulator
is "bap" and dataset is "Test dataset". If any of the forementioned is missing
from the database, it will be created.

NOTE: The figure filenames are wrapped in single quotes (') instead of double
quotes (") to make sure ${probe_name} is not replaced by the shell.


insert_supplementary_data.py
----------------------------

Let's use the same 'results.txt' file as in the previous script:

FBgn ischip hasinsitu isinsitu baseline gpdisim gpsim
FBgn0000008 0 0 0 -69.308261 -100.719304 19.021085
FBgn0000011 0 0 0 -622.260758 -16.649425 57.799397
FBgn0000014 1 1 1 -94.052995 -51.492857 23.269117
FBgn0000015 1 0 0 -219.278879 -24.023653 38.973297
FBgn0000017 0 0 0 -57.974217 -87.721620 -3.315447
FBgn0000018 0 0 0 -84.989078 -116.390492 6.232027
FBgn0000022 0 1 0 -75.916914 -48.959545 4.631974
FBgn0000024 0 1 0 -4.333182 -35.734065 50.582057

Hasinsitu values of the genes can be added to the database with the following
command:

$ python insert_supplementary_data.py -f results.txt -c 3 database.sqlite "hasinsitu"

Option '-c' is used to give the correct column.

insert_zscores.py
-----------------

Assume the file 'zscores.txt' contains the following 9 lines:

FBgn zscore
FBgn0000008 0.0
FBgn0000011 0.5
FBgn0000014 1.0
FBgn0000015 0.7
FBgn0000017 0.9
FBgn0000018 2.0
FBgn0000022 0.2
FBgn0000024 0.3

The z-scores of these genes can be added to the database with command:

$ python insert_zscores.py -f zscores.txt database.sqlite "Test dataset"

If dataset "Test dataset" is missing from the dataset, it will be created.

