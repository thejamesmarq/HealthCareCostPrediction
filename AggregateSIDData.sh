#!/bin/sh

set -e
echo "Identifying beneficiaries to use from "$1
python MakeCohort.py $1 $2
echo "Joining utilization and comorbidity data"
Rscript merge_data.r $1 $2
echo "Aggregating beneficiary data"
python AggregateBeneficiaries.py $1 $2