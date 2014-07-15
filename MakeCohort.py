import csv, sys, os

#write a dictionary as a csv
def writeDict(out_dict,header,outpath):
	with open(outpath, "wb") as outfile:
		writer = csv.writer(outfile)

		writer.writerow(header)

		for key in out_dict.keys():
			for item in out_dict[key]:
				writer.writerow(item)

#get the path of the CORE file
#def getCorePath(year):
#	return "./Data/WA_SID_" + str(year) + "_CORE.csv"

#create dictionaries keyed by VisitLink
def makeDicts(path,year):
	bene_dict = {}
	colnames = {}
	header = None

	filename = path+slash+"WA_SID_"+str(year)+"_CORE.csv"

	with open(filename, "rb") as infile:
		reader = csv.reader(infile)

		header = reader.next()
		colnames["AMONTH"] = header.index("AMONTH")
		colnames["VisitLink"] = header.index("VisitLink")
		colnames["TRAN_IN"] = header.index("TRAN_IN")

		#pull lines into dictionary, discard transfer cases
		for line in reader:
			if int(line[colnames["VisitLink"]]) not in bene_dict:
				if int(line[colnames["TRAN_IN"]]) != 1:
					bene_dict[int(line[colnames["VisitLink"]])] = [[x.strip() for x in line]]
			else:
				if int(line[colnames["TRAN_IN"]]) != 1:
					bene_dict[int(line[colnames["VisitLink"]])].append([x.strip() for x in line])

	return bene_dict, colnames, header

#discard beneficiaries which don't have at least one q1 to q3 admit and one q4 admit
def getCandidates(bene_dict, colnames):
	#q4_months = [10,11,12]
	#q1toq3_months = [1,2,3,4,5,6,7,8,9]

	for key in bene_dict.keys():
		q1toq3 = q4 = 0
		for item in bene_dict[key]:
			if int(item[colnames["AMONTH"]]) > 9:
				q4 = 1
			elif int(item[colnames["AMONTH"]]) <= 9:
				q1toq3 = 1
		if not (q1toq3 == 1 and q4 == 1):
			del bene_dict[key]

#main method
def main(year,path,slash):

	bene_dict, colnames, header = makeDicts(path,year)

	getCandidates(bene_dict, colnames)

	writeDict(bene_dict, header, path+slash+str(year)+"_candidates.csv")

#script takes three arguments: the year of the SID CORE file and the file's directory and how to split the data (quarters or semesters)
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

	main(year,path,slash)
