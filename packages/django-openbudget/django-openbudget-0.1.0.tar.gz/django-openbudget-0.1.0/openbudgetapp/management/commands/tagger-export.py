from django.core.management.base import BaseCommand, CommandError
from openbudgetapp.models import *
import sqlite3
from datetime import *
import csv
	
	
class Command(BaseCommand):
	args = '<basename for export>'
	help = 'Creates an input and output data file suitable for automatic tagging'

	def handle(self, *args, **options):
			
		if len(args) < 1:
			raise CommandError('Requires arguments %s' % self.args)

		taggerout=args[0]

		
		#self.stdout.write('.Creating splits\n')
		
		accounts=Account.objects.all()
		
		inputWriter = csv.writer(open('taggerin.csv', 'wb'), delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		outputWriter = csv.writer(open('taggerout.csv', 'wb'), delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		
		guids=accounts.values('guid')
	
		import collections
		import string

		print "Num labels:%d" % len(guids)
	
		
		print "Creating word dict..."
		#create a word dictionary
		w=""
		for a in accounts:
			splits=a.split_set.all()
			for s in splits:
				
				desc=s.tx.description
				w+=" " + str(desc)
		
		w = w.translate(string.maketrans("",""), string.punctuation).lower()
		word_dict={}
		
		for word,freq in collections.Counter(w.split()).items():
		        word_dict[word]=freq
		
		i=0
		for a in accounts:
			print ".Processing %s" % a.name
			splits=a.split_set.all()
			for s in splits:
				
			
				dom=s.tx.postdate.day
				m=s.tx.postdate.month
				desc=s.tx.description
				value=s.value
				tag=i
				
				print "..building word count"
				#count occurence of word in description
				w_desc=str(desc)
				w_desc=w_desc.translate(string.maketrans("",""), string.punctuation).lower()
				w_desc.split()
				line=[]	
				for word in word_dict:
				    line.append(w_desc.count(word))    
					
			
				inputWriter.writerow(line)
				outputWriter.writerow([tag])
		
			i+=1
	
	