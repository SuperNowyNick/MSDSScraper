import sys
import getopt
import requests
import csv
import re
from pathlib import Path
import logging
import time

def main(argv):
	caslist = ''
	directory = ''
	language = 'pl'
	notfound = []
	
	try:
		opts, args = getopt.getopt(argv,"hi:d:",["ifile=","idir=",])
	except getopt.GetoptError:
		print("No csv file with CAS numbers given")
		print("Usage: msdsscraper.py -i <input.csv> [options]")
		print("Type msdsscraper.py -h for help")
		exit(2)

	for opt, arg in opts:
		if(opt == "-h"):
			print("MSDS checker. Takes a CAS number list and checks if they are present in current dir.")
			print("Usage: msdsscraper.py -i <input.csv> -d <directory>")
		if(opt == "-i"):
			csvfile = open(arg)
			caslist = csv.reader(csvfile, delimiter=' ')
			print("CAS list loaded:")
		if(opt == "-d"):
			directory = arg
	
	if(caslist == ''):
		print("No csv file with CAS numbers given")
		exit(2)
		
	print("Checking directory")
	if len(directory)>0:
		directory.rstrip("/")
		directory.rstrip("\\")
		directory="".join([directory, "\\"])
	for row in caslist:
		for cas in row:
			f = Path(directory+cas+".pdf")
			if not f.is_file():
				print("file "+ directory+cas+".pdf"+ " not found")
				notfound.append(cas)
	print("Finished!")
	print("".join([str(len(notfound)), " compounds not found."]))
	with open("notfound.csv", "w") as exportfile:
		for cas in notfound:
			print("\""+cas+"\"", file=exportfile)
	

		
if __name__ == "__main__":
   main(sys.argv[1:])