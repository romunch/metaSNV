#!/usr/bin/env python
import os               # interacting with operating system
import sys		# interact with system commandline 
import time		# print current date/time
import argparse		# manage command line options and arguments
import glob

import numpy as np
import pandas as pd


basedir = os.path.dirname(os.path.abspath(__file__))


#############################
# Parse Commandline Arguments
#############################
def get_arguments():
	'''
	Get commandline arguments and return namespace
	'''
	## Initialize Parser
	parser = argparse.ArgumentParser(prog='metaSNV_post.py', description='metaSNV post processing', epilog='''Note:''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	
# Not Showns:
	parser.add_argument('--version', action='version', version='%(prog)s 2.0', help=argparse.SUPPRESS)
	parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)

	
#	TODO: POPULATION STATISTICS
	## Population Statistics (Fst - ):
#	parser.add_argument("-f", "--fst", action="store_true")
	## pNpS ratio:
#	parser.add_argument("-n", "--pnps", action="store_true")
	
	
# OPTIONAL arguments:
	parser.add_argument('-b', metavar='FLOAT', type=float, help="Coverage breadth: Horizontal genome coverage percentage per sample per species", default=40.0)
	parser.add_argument('-d', metavar='FLOAT', type=float, help="Coverage depth: Average vertical genome coverage per sample per species", default=5.0)
	parser.add_argument('-m',metavar='INT', type=int, help="Minimum number of samples per species", default=2)
	parser.add_argument('-c',metavar='FLOAT', type=float, help="FILTERING STEP II: minimum coverage per position per sample per species", default=5.0)
	parser.add_argument('-p',metavar='FLOAT', type=float, help="FILTERING STEP II: required proportion of informative samples (coverage non-zero) per position", default=0.50)
		
# REQUIRED  arguments:
	parser.add_argument('projdir', help='project name', metavar='Proj')
	
	return parser.parse_args()

	##############################

def debugging(taxids_of_interest, header_cov):
	'''Sanity check for the Dict of TaxID:Samples'''
	
	nr_keys = 0
	taxids_of_interest = []
	for key in samples_of_interest:
		nr_keys += 1
		taxids_of_interest.append(key)

	taxids_of_interest.sort()
	print("DEBUGGING:\nNr_TaxIDs_of_Interest.keys: {}".format(nr_keys))
	print(taxids_of_interest)
#	print("\n")
#   print("nr_TaxIDs_of_Interest.keys: {}".format(nr_keys))

	header = "\t".join(header_cov)
	print("DEBUGGING: no. samples in header: {}\n".format(len(header_cov)))
#   print("header: {}".format(header))

	sys.exit("only filter 1")

	
def file_check():
	''' Check if required files exist (True / False)'''
	args.coverage_file = args.projdir+'/'+args.projdir+'.all_cov.tab'
	args.percentage_file = args.projdir+'/'+args.projdir+'.all_perc.tab'
	args.all_samples = args.projdir+'/'+'all_samples'

	print("Checking for necessary input files...")
	if os.path.isfile(args.coverage_file) and os.path.isfile(args.percentage_file):
		print("found: '{}' \nfound:'{}'".format(args.coverage_file, args.percentage_file))
	else:
		sys.exit("\nERROR: No such file '{}',\nERROR: No such file '{}'".format(args.coverage_file, args.percentage_file))

	if os.path.isfile(args.all_samples):
		print("found: '{}'\n".format(args.all_samples))
	else:
		sys.exit("\nERROR: No such file '{}'".format(args.all_samples))

def print_arguments():
	## Print Defined Thresholds:
	print("Options:")
	if args.b:
		print("threshold: percentage covered (breadth) {}".format(args.b) )
	if args.d:
		print("threshold: average coverage (depth) {}".format(args.d) )
	if args.m:
		print("threshold: Min. number samples_of_interest per taxid_of_interest {}".format(args.m) )
	if args.c:
		print("threshold: Min. position coverage per sample within samples_of_interest {}".format(args.c) )
	if args.p:
		print("threshold: Min. proportion of covered samples in samples_of_interest {}".format(args.p) )	
	print("")

###############################
## FILTER I: Count SAMPLES_OF_INTEREST per TAXON_OF_INTEREST
#	Example: "Which taxon has at least 10 SoI?"
#  --Coverage Conditions:
#	Sample of Interest:
#		1. breadth > 40 %  
#		2. depth   >  5 X
#  --Min. number Samples:
#		3. min samples/TaxID > 10
def relevant_taxa(args):
	'''function that goes through the coverage files and determines taxa and samples of interest'''

	samples_of_interest = {}
	with open(args.coverage_file, 'r') as COV, open(args.percentage_file, 'r') as PER:
		header_cov = COV.readline().split()
		header_per = PER.readline().split()
		COV.readline()	# skip second row in COV_FILE
		PER.readline()  # skip second row in PER_FILE

		# Check if header match:
		if header_cov != header_per:
			sys.exit("ERROR: Coverage file headers do not match!")  #Exit with error message

		# Read taxon by taxon (line by line) check coverage conditions (thresholds)
		for cov,perc in zip(COV,PER):	# Line_cov: TaxID \t cov_valueS1 \t cov_value_S2[...]\n (no white spaces)	
			cstring = cov.split()
			pstring = perc.split()	
			cov_taxID = cstring.pop(0)
			perc_taxID = pstring.pop(0)
			coverage = list(map(float, cstring))  # convert list_of_strings 2 list_of_floats (TaxID=INT!)
			percentage = list(map(float, pstring))  # convert list_of_strings 2 list_of_floats
			sample_count = 0
			sample_names = []

#			print(cov_taxID,perc_taxID)

			if cov_taxID != perc_taxID:	# check if taxIDs match!
				sys.exit("ERROR: TaxIDs in the coverage files are not in the same order!")

			for c,p in zip(coverage,percentage): # two arrays with floats (taxID pop[removed]) 
				sample_count += 1

				if c >= args.d and p >= args.b:	

					sample_names.append(header_cov[sample_count-1]) # starting at 0 in array

				if sample_count == len(header_cov) and len(sample_names) >= args.m:

					samples_of_interest[cov_taxID] = sample_names

	return {'SoI':samples_of_interest, 'h':header_cov}#return dict()
	COV.close()
	PER.close()
	#################################
	# FILTER I: END 'returns(<'samples_of_interest', type=dict>)'
	#################################



def header_comparison(header_cov):
	'''Comparing the sample order in the coverage and all_samples file'''

	# sort snp_indices by sample_of_interest names
	header = "\t".join(header_cov)
	#print("\nNr.Samples_cov_header: {}".format(len(header_cov)))
	#print("cov_header: {}\n\n".format(header_cov[:10]))
	#print("\ncov_header: {}\n {}\n\n".format(len(header_cov),header))

	### read <all_samples> for snp_file header:
	all_samples = open(args.all_samples,'r')
	snp_header = all_samples.read().splitlines()
	snp_header = [i.split('/')[-1] for i in snp_header] #get name /trim/off/path/to/sample.name.bam
	snp_header_joined = "\t".join(snp_header)
	
	#print("Nr.Samples in (all_samples): {}".format(len(snp_header)))
	#print("all_samples: {}\n".format(snp_header[:10]))
	
	# Compare the sample order in ALL.COV/ALL.PERC and all_samples
	#print("Comparing headers..")
	#if header == snp_header_joined:
	#	print("Headers match nicely\n")
	#else:
	#	print("CAUTION: Header in COV_FILE does not match the order of samples in the SNP_FILES,\n\t no problem, we took care of it!\n")
	
	return snp_header	

	
#################################
## FILTER II: ACQUIRE SNPs WITH SUFFICIENT OCCURRENCE WITHIN SAMPLES_OF_INTEREST
#  --SNP Conditions (Default):
#           1. Position covered by at least (5) reads
#           2. Position present in at least 50 % of the accepted samples_of_interest

def filter_two(args, snp_header, snp_files, outdir):
	'''position wise filtering'''
	
	header_taxID = ''
	snp_taxID = '_'
#	print(locals())
	for best_split_x in snp_files:
	
		with open(best_split_x, 'r') as file:
			for snp_line in file:	#position wise loop
				snp_taxID = snp_line.split()[0].split('.')[0]#Name of Genome change from . to ]

			## SPECIES FILTER:
				if snp_taxID not in samples_of_interest.keys():#Check if Genome is of interest
				
					continue #Taxon is not relevant, NEXT!
	
				else:
			## SAMPLE FILTER: only load samples with enough coverage
					sample_list = samples_of_interest[snp_taxID]#Load Sample List
					# !!! Sample order, get indices - INDICES based on ORDER in COV/PERC file!!!
					sample_indices = []
					for name in sample_list:

						sample_indices.append(snp_header.index(name))
			## POSITION FILTER:
			# Positions with sufficient coverage (c) and support (p, proportion) in the discovery set (covered samples).
				# Discovery set: sufficiently covered samples
				#..site coverage >= cX
				#..proportion 	>= p% (SoIs)
					whole_line = snp_line.split()
					site_coverage = list(map(int, whole_line[4].split('|'))) # Site coverages as list of ints
					nr_good = 0
					for index in sample_indices:
						if site_coverage[index] < args.c or site_coverage[index] == 0:
							continue#NOT enough coverage depth at position in sample, no increment
						else:
							nr_good += 1
				#FILTER: Position incidence with sufficient coverage:
					if float(nr_good)/len(sample_indices) < args.p:#if snp_incidence < x % drop SNP
	
						continue#mainly uninformative position, SNP incidence < x %, SNP droped!
	
					else:
					# CALCULATE SNP ALLELE FREQUENCY:
						# If at least one position passed cutoffs open file (if new TaxID):
						if header_taxID != snp_taxID:
							if 'outfile' in locals():
								print("closing: {}".format(header_taxID) )
								outfile.close()
							outfile = open(outdir+'/'+'%s.filtered.freq' % snp_taxID, 'w')
							print("Generating: {}".format(outdir+'/'+'%s.filtered.freq' % snp_taxID))
							outfile.write('\t' + "\t".join(sample_list) + '\n')
		
							header_taxID = snp_taxID#Jump to current TaxID
			
					#Loop through alternative alleles [5](comma separated):
						line_id = ":".join(whole_line[:4])#line_id composed of CHROM:REFGENE:POS:REFBASE
						reference_base = whole_line[3]
						alt_bases_totalcov = []#total coverage per alt allele
						#VCF format
	
						#LOOP Start:
						for snp in whole_line[5].split(','):
	
							xS = snp.split('|')
							snp_coverage = list(map(float, xS[3:]))#coverage string (unfiltered!)
	
							#Sanity check:	
							if len(site_coverage) != len(snp_coverage):
								print("ERROR: SNP FILE {} is corrupted".format(best_split_x))
								sys.exit("ERROR: Site coverage and SNP coverage string have uneven length!")
	
							#Compute allele frequency tables:
							alt_base = snp.split('|')[1]#alternative base	
	
							#FREQUENCY Computation
							total_reads = 0
							snp_frq = []#frequencies for SNPs (pos >5X in at least 50% of the SoIs)
							for index in sample_indices:
	
						#prevent division by zero! TODO:Notify usr about Nonsense Value (f.i. -c = 0!	
								if site_coverage[index] >= args.c and site_coverage[index] != 0:
	
									snp_frq.append(snp_coverage[index]/site_coverage[index])
	
								else:
									snp_frq.append(-1)	
	
					# WRITE OUTPUT Allele Frequencies (Default)
							outfile.write(":".join(snp_line.split()[:4])+'>'+alt_base +':'+ xS[2] + '\t' + "\t".join(str(x) for x in snp_frq) + '\n')

#if header_taxID != snp_taxID:
	if 'outfile' in locals():
		#print("closing: last = {}".format(header_taxID))
		outfile.close()

def l1nonans(d1,d2):
    return np.abs(d1 - d2).mean()

def alleledist(d1,d2, threshold=.6):
    return (np.abs(d1 - d2) > threshold).mean()

def computeAllDist(args):

    print "Computing distances"
    allFreq = glob.glob(args.projdir + '/filtered/pop/*.freq')
    for f in allFreq:

	data = pd.read_table(f, index_col=0, na_values=['-1']).T
    	dist = [[l1nonans(data.iloc[i], data.iloc[j]) for i in range(len(data))] for j in range(len(data))]
    	dist = pd.DataFrame(dist, index=data.index, columns=data.index)

    	dist.to_csv(args.projdir+'/distances/'+'%s.mann.dist' % f.split('/')[-1].replace('.freq',''), sep='\t')

    	dist = [[alleledist(data.iloc[i], data.iloc[j]) for i in range(len(data))] for j in range(len(data))]
    	dist = pd.DataFrame(dist, index=data.index, columns=data.index)

    	dist.to_csv(args.projdir+'/distances/'+'%s.allele.dist' % f.split('/')[-1].replace('.freq',''), sep='\t')

if __name__ == "__main__":
#	print("globals: {}".format(globals()))

	args = get_arguments()
	print_arguments()
	file_check()

	if args.debug:
		print_arguments()

#==========================================
# Filtering I - Determine Taxa of Interest:
#==========================================

	samples_of_interest = relevant_taxa(args)['SoI']
	header_cov = relevant_taxa(args)['h']

	if args.debug:
		debugging(samples_of_interest, header_cov)#needs: samples_of_interest,header_cov


#=========================================
# Filtering II - Position wise filtering
#=========================================
	snp_header = header_comparison(header_cov) #not necessary?! we identify it anyways..

	filter_two(args, snp_header,glob.glob(args.projdir + '/snpCaller/called*'),args.projdir + '/filtered/pop')
	filter_two(args, snp_header,glob.glob(args.projdir + '/snpCaller/indiv*'),args.projdir + '/filtered/ind')

	computeAllDist(args)
