import csv, numpy, sys, os

#utility to check if string is numeric
def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#utility to check if string is an int
def isInt(s):
	if "." in s:
		return False

	try:
		int(s)
		return True
	except ValueError:
		return False

#aggregate data by beneficiary
def aggregate(year, path, slash):

	ben_dict = dict()
	col_dict = dict()
	agg_dict = dict()
	header = []
	test_months = [10,11,12]

	with open(path+slash+year+"_candidates.csv","rb") as infile:
		reader = csv.reader(infile)

		#Get column names
		for index, name in enumerate(reader.next()):
			col_dict[name] = index

		#group all visitlinks
		for line in reader:
			if line[col_dict["VisitLink"]] not in ben_dict:
				ben_dict[line[col_dict["VisitLink"]]] = [line]
			else:
				ben_dict[line[col_dict["VisitLink"]]].append(line)

	#initialize diagnoses and procedures and revcode and comorbidity indeces
	diagnoses = []
	diag_indeces = [y for x,y in col_dict.iteritems() if "DXCCS" in x]

	procedures = []
	proc_indeces = [y for x,y in col_dict.iteritems() if "PRCCS" in x]

	revcodes = []
	rev_indeces = [y for x,y in col_dict.iteritems() if "REVCD" in x]

	comorb_indeces = [y for x,y in col_dict.iteritems() if "CM_" in x]
	comorbidities = [x for x,y in col_dict.iteritems() if "CM_" in x]

	#determine appropriate diagnoses, procedures, and revcodes
	for beneficiary, values in ben_dict.iteritems():
		for entry in values:
			diagnoses.extend([entry[i] for i in diag_indeces if isInt(entry[i])])
			procedures.extend([entry[i] for i in proc_indeces if isInt(entry[i])])
			revcodes.extend([entry[i] for i in rev_indeces if isInt(entry[i])])

	#ensure that the codes are unique
	diagnoses = set(diagnoses)
	procedures = set(procedures)
	revcodes = set(revcodes)

	#build header
	diag_header = ["DXCCS_" + str(x) for x in diagnoses]
	proc_header = ["PRCCS_" + str(x) for x in procedures]
	rev_header = ["REVCD_" + str(x) for x in revcodes]

	header.append("VisitLink")
	header.extend(diag_header)
	header.extend(proc_header)
	header.extend(rev_header)
	header.extend(comorbidities)
	header.append("age")
	header.append("female")
	header.append("race")
	header.append("total_diagnoses")
	header.append("total_procedures")
	header.append("chronic_conditions")
	header.append("train_charge")
	header.append("test_charge")

	data = []

	for beneficiary, values in ben_dict.iteritems():

		test_charge = 0
		train_charge = 0
		diag_dict = {}
		proc_dict = {}
		rev_dict = {}
		comorb_list = [0]*len(comorb_indeces)
		age = None
		gender = None
		race = None
		chronics = []

		#aggreag
		for entry in values:

			if not entry[col_dict["AGE"]].isspace():
				age = entry[col_dict["AGE"]]

			if not entry[col_dict["FEMALE"]].isspace():
				gender = entry[col_dict["FEMALE"]]

			if not entry[col_dict["RACE"]].isspace():
				race = entry[col_dict["RACE"]]

			if int(entry[col_dict["AMONTH"]]) in test_months:
				if int(entry[col_dict["TOTCHG"]]) >= 0:
					test_charge += int(entry[col_dict["TOTCHG"]])
			else:
				if int(entry[col_dict["TOTCHG"]]) >= 0:
					train_charge += int(entry[col_dict["TOTCHG"]])

				for value in [entry[i] for i in diag_indeces]:
					if value not in diag_dict:
						diag_dict[value] = 1
					else:
						diag_dict[value] += 1

				for value in [entry[i] for i in proc_indeces]:
					if value not in proc_dict:
						proc_dict[value] = 1
					else:
						proc_dict[value] += 1

				for value in [entry[i] for i in rev_indeces]:
					if value not in rev_dict:
						rev_dict[value] = int(entry[i+100]) if float(entry[i+100])>=0 else 0
					else:
						rev_dict[value] += int(entry[i+100]) if float(entry[i+100])>=0 else 0

				comorb_list = [int(x) | int(y) if isNumber(y) else x for x, y in zip(comorb_list,[entry[i] for i in comorb_indeces])]

				chronics.append(int(entry[col_dict["NCHRONIC"]]))

		row = []
		row.append(beneficiary)
		for item in diagnoses:
			if item in diag_dict:
				row.append(diag_dict[item])
			else:
				row.append(0)
		for item in procedures:
			if item in proc_dict:
				row.append(proc_dict[item])
			else:
				row.append(0)
		for item in revcodes:
			if item in rev_dict:
				row.append(rev_dict[item])
			else:
				row.append(0)
		row.extend(comorb_list)
		row.append(age)
		row.append(gender)
		row.append(race)
		row.append(sum(diag_dict.values()))
		row.append(sum(proc_dict.values()))
		row.append(numpy.mean(chronics))

		row.append(train_charge)
		row.append(test_charge)

		data.append(row)

	#write aggregated data to disk
	with open(path+slash+year+"_candidates_extra.csv","wb") as outfile:
		writer = csv.writer(outfile)

		writer.writerow(header)
		writer.writerows(data)

#main
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "Script takes two arguments: year data and file's directory "
		sys.exit()

	if os.name == 'nt':
		slash = "\\"
	else:
		slash = "/"

	year = sys.argv[1]
	path = sys.argv[2]

	while (path[-1] == '\\' and os.name =='nt') or (path[-1] == '/' and os.name != 'nt'):
		path = path[:-1]

	aggregate(year,path,slash)


