This repository contains code for experiments in Healthcare Cost Prediction
____

Aggregate data by beneficiary:
This step is needed prior to running experiments. Identifies candidate beneficiaries and joins in needed data.

$year <- year of data to use  
$path <- location of data

	sh AggregateSIDData $year $path

Run experiments:
Experiments can be run from command line or using GUI such as RStudio. To run from command line, uncomment lines 20-22 in run_experiments.R.
Note that running from command line will perform data preprocessing steps each run. GUI is recommended.

To run from command line:

$year <- year of data to use  
$path <- location of aggregated data

	RScript run_experiments.R $year $path

Script is currently set up to run experiments using 100 tree Random Forests via 10 times 10 fold cross validation. Other models can be trained by uncommenting models below line 182.

Additional notes:  
*If you wish to run experiments over a sample of the aggregated data, uncomment lines 150-151.
