

def logger(text):
	if logHuh == True:
		print(text)

def handleArgs(st):
	f=''
	for i in range(st, len(sys.argv)):
		f = f + sys.argv[i] + ' '
	nation=f.strip()

	#check if it exists
	exists=False
	for i in range(len(cdList)):
		if nation == cdList[i]['country']:
			exists=True
	if exists==False:
		print('Error: Invalid country name entered \ntry Capitalizing the first letter')
		print('enter \"list\" as argument to see all valid countries')
		raise SystemExit()
	return nation

def listValidCountries():
	for i in range(len(cdList)):
		print(cdList[i]['country'])

def getreply(payload):
	
	url = 'https://en.wikipedia.org/w/api.php?'
	# get stuff from url while injecting payload
	import requests
	logger('###log: Making API request to wikipedia...' )
	try:
		r = requests.get(url=url, params=payload)
	except requests.exceptions.RequestException :
		print('Error: Could not establish connectiion to Wikipedia\nCheck your internet connection and try again')
		raise SystemExit()
	# jData = json.loads(r.content)
	jData = r.json()
	return (jData)

def getRefTable():
	try:
		import a1_weightsTable
		logger('###log: imported a1_weightsTable.py')
	except ImportError:
		logger('###log: could not import a1_weightsTable.py ; Using hardcoded weights ')
		nTable = [
			{'weight': '1.0', 'templates': ['free'], 'desc': 'Freedom of Movement'},
			{'weight': '0.9', 'templates': ['yes','yes '], 'desc': 'Visa Free'},
			{'weight': '0.7', 'templates': ['Optional', 'yes-no'], 'desc': 'Visa on Arrival'},
			{'weight': '0.5', 'templates': ['yes2'], 'desc': 'eVisa'},
			{'weight': '0.4', 'templates': ['no','no ', 'n/a'], 'desc': 'Visa required'},
			{'weight': '0.0', 'templates': ['black', 'BLACK'], 'desc': 'Banned'},
		]
		#TODO create table if no exstance
		# write weights table to file
		import pprint
		c_list = open('a1_weightsTable.py', 'w')
		c_list.write('refTable = ' + pprint.pformat(nTable))
		c_list.close()
		logger('###log: created a1_weightsTable.py ')
	else:
		nTable = a1_weightsTable.refTable

	return nTable

def find_demonym(nation):

	flag = False
	for i in range(len(cdList)):
		if cdList[i]['country'] == nation:
			flag = True
			return cdList[i]['demonym']
	if flag == False:
		print('nation & demonym of '+nation+' not found in country_list')

def getGDPtable():	#get info from wikipedia , get wikitext from that , creates the GDPtable and returns it

	try:
		import a2_GDPtable
		logger('###log: imported GDPtable')
	except (ImportError, SyntaxError):
		logger('###log: cound not import GDPtable')
		payload = {
			"action": "query",
			"format": "json",
			"prop": "revisions",
			"titles": "List_of_countries_by_GDP_(nominal)",
			"rvprop": "content",
			"rvlimit": "1",
			"rvsection": "1"
		}
		jData = getreply(payload)

		import a1_peeFormatFs

		# go inside the nest
		jData = jData['query']
		jData = jData['pages']
		pageNo = list(jData)[0]
		jData = jData[pageNo]
		jData = jData['revisions']

		contents = (str)(jData[0])
		contents = a1_peeFormatFs.unbrace(contents)

		### make a list of all the countries and their GDPs (newest available)

		# use regex to find
		import re
		x = re.compile(r'{{[fF]lag\|.*?}}.*?\|\|.*?[\|]{1}?.*?[\|]{1}?[\-}]{1}?', re.DOTALL)

		gdpDATA = x.findall(contents)
		del contents

		GDPtable = []
		for i in range(len(gdpDATA)):
			t = gdpDATA[i]
			# snip tail text
			t = (t[0:len(t) - 4])
			# find country
			y = re.compile(r'{{[fF]lag\|.*?}}')
			theCountry = y.findall(t)[0]
			theCountry = theCountry[7:len(theCountry) - 2]

			# replace accented names with a unique substring without accents to match
			if 'voire' in theCountry:
				theCountry = 'Ivory Coast'
			if 'ncipe' in theCountry:
				theCountry = 'Sao Tome and Principe'
			if 'Cura' in theCountry:
				theCountry = 'Curacao'

			# find gdp
			y = re.compile(r'{{nts\|.*?}}')
			p = y.findall(t)
			theGDP = ''
			if len(p) <= 0:
				j = len(t) - 1
				while j >= 0:
					if t[j] == '|':
						theGDP = t[j + 1:len(t)]
						break
					j = j - 1
			else:
				theGDP = p[0]
				theGDP = theGDP[6:len(theGDP) - 2]
			# remove commas from theGDP and convert to integer
			theGDP = float(''.join(i for i in theGDP if i.isdigit()))
			theGDP = float("{0:.3f}".format(theGDP))

			aDic = {'Country': theCountry, 'GDP': theGDP}
			GDPtable.append(aDic)
		# write gdp table to file
		import pprint
		c_list = open('a2_GDPtable.py', 'w')
		c_list.write('#uses the first gdp that matches the country \n')
		c_list.write('#Ivory Coast, Sao Tome and Principe and Curacao may have been de accented \n')
		c_list.write('GDPtable = ' + pprint.pformat(GDPtable))
		c_list.close()
		logger('###log: created a2_GDPtable.py ')
		
	else:
		GDPtable = a2_GDPtable.GDPtable
	return (GDPtable)

def find_gdp(nation):
	flag = False
	for i in range(len(gTable)):
		if (gTable[i]['Country'] in nation) or (nation in gTable[i]['Country']):
			flag = True
			return gTable[i]['GDP']
	if flag == False:
		logger('###error: gdp for '+nation+' not found in gTable')

class country:
	__name = ''
	__gdp  = 0
	#__pppCapita = 0
	#__population = 0
	__gdpAxsScore = 0.0
	__visaScoreList = []    #stores dictionaries with keys, country and visaScore 
	__demonym = ''
	__url = ''
		
	def wiki2wText(self,nationality):
		# get info from wikipedia and returns wikitext

		# check if wikitext exists
		PATH = './WT-' + nationality + '.txt'

		if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
			logger("###log: wikitext file exists and is readable for "+ nationality)
		else:
			# find rvsection
			logger("###log: wikitext file is not readable for "+ nationality)
			payload = {
				"action": "parse",
				"format": "json",
				"prop": "sections",
				"page": 'Visa_requirements_for_' + nationality + '_citizens'
			}
			t = getreply(payload)

			t = t['parse']
			sections = t['sections']

			f = False
			for i in range(len(sections)):
				# print(sections[i]['anchor']+' is anchor at index '+i+' for '+nationality)
				if sections[i]['anchor'].lower() == 'visa_requirements' or sections[i]['anchor'].lower() == 'visa_requirements_by_country':
					rvsection = sections[i]['number']
					f = True
					break
			if f == False:
				logger('###log: visa_requirements section not found in wiki page for ' + nationality)

			payload = {
				"action": "query",
				"format": "json",
				"prop": "revisions",
				"titles": 'Visa_requirements_for_' + nationality + '_citizens',
				"rvprop": "content",
				"rvlimit": "1",
				"rvsection": rvsection
			}
			jData = getreply(payload)

			import a1_peeFormatFs

			# go inside the nest
			jData = jData['query']
			jData = jData['pages']
			pageNo = list(jData)[0]
			jData = jData[pageNo]
			jData = jData['revisions']

			contents = (str)(jData[0])
			# contents=a1_peeFormatFs.unbrace(a1_peeFormatFs.unbrace(contents))

			# write to file with prettiness
			a1_peeFormatFs.ppWrite(contents, 'WT-'+nationality )
			logger('###log: got api Data / wikiTable for the ' + nationality + ' citizens ')
			return contents

	def getTotGDP_Access(self,currentNation, WT):	#gets visa score for the country
		

		def getScore(cvList, currentNation):	#create list of dictionaries and find final score

			def findWeight(level):

				flag = False
				for i in range(len(refTable)):
					found = False
					for j in range(len(refTable[i]['templates'])):
						if level.lower() == refTable[i]['templates'][j].lower():
							found = True
							break
					if found:
						return float("{0:.3f}".format((float(refTable[i]['weight']))))
				if flag == False:
					logger('###error: template not found in refTable. template was ' + level)
					return (0)

			GDP_AccessList = []
			tDic = {}
			total_GDP_Access = 0
			# find for currentNation
			found = 0
			for j in range(len(gTable)):

				if (currentNation in gTable[j]['Country']) or (gTable[j]['Country'] in currentNation):
					tsuff = gTable[j]['GDP'] * findWeight('free')
					tDic = {'Country': currentNation, 'VisaRequired': 'free', 'GDP_Access': float("{0:.3f}".format(tsuff))}
					GDP_AccessList.append(tDic)
					total_GDP_Access = total_GDP_Access + gTable[j]['GDP']
					found = 1
					break

			if found == 0:
				logger('###log: no GDP_Access for ' + currentNation + ' to itself')

			# now the rest of the countries
			for i in range(len(cvList)):
				found = 0
				for j in range(len(gTable)):

					if (cvList[i]['country'] in gTable[j]['Country']) or (gTable[j]['Country'] in cvList[i]['country']):
						
						tsuff = gTable[j]['GDP'] * findWeight(cvList[i]['visaTemplate'])
						tsuff = float("{0:.3f}".format(tsuff))
						tDic = {'Country': cvList[i]['country'], 'VisaRequired': cvList[i]['visaTemplate'],
								'GDP_Access': tsuff}
						GDP_AccessList.append(tDic)
						total_GDP_Access = total_GDP_Access + tsuff
						found = 1
						break
				if found == 0:
					logger('###log: no GDP_Access for ' + currentNation + ' to ' + cvList[i]['country'])

			import pprint
			c_list = open('GdpAxs'+find_demonym(currentNation) + '.py', 'w')
			c_list.write('#GDP Access List for' + currentNation + ' \n')
			c_list.write('GDPtable = ' + pprint.pformat(GDP_AccessList))
			c_list.close()
			logger('###log: created GdpAxs' + currentNation + '.py ')
			self.__visaScoreList = GDP_AccessList
			return total_GDP_Access

		def createCV_List(cvList): # create list of dictionaries of country and template(visaReq)
			
			neuCV_list = []
			cvDic = {}

			cExhauster=[]
			for i in range(len(cdList)):
				cExhauster.append(cdList[i]['country']) #use to make sure countries are only accesed once

			for i in range(len(cvList)):

				###find Country
				x = re.compile(r'{{ *?[fF][lL][aA][gG] *[|].*?}}')
				c = x.findall(cvList[i])[0]
				# find name
				x = re.compile(r'name=.*?}')
				if len(x.findall(c)) != 0:
					c = x.findall(c)[0]
					c = c[5:-1]
				else:
					# remove state
					x = re.compile(r'lag\|[^}]*?\|')
					if len(x.findall(c)) != 0:
						c = x.findall(c)[0]
						c = c[4:-1]
					else:
						# find regularly
						x = re.compile(r'lag\|[^}]*?}')
						c = x.findall(c)[0]
						c = c[4:-1]

				###find visa template
				beginer = 0
				ender = 0
				saveEnd = False
				for j in range(5, len(cvList[i]) - 2):
					if cvList[i][j] == '{' and cvList[i][j + 1] == '{':
						beginer = j + 2
						# print('found { {')
						saveEnd = True
					elif cvList[i][j] == '|' and saveEnd == True:
						ender = j
						# print('found | ')
						break

				v = cvList[i][beginer:ender]

				cvDic = {'country': c, 'visaTemplate': v}

				#check if the country is in country_list 
				there=False
				for i in range(len(cExhauster)):
					if c==cExhauster[i] :
						there=True
						cExhauster.remove(c)
						break
					elif 'ncipe' in c or 'voir' in c:
						there=True
						#hmm
						break
				if there==True:
					neuCV_list.append(cvDic)
				else: 
					logger('###log: excluded '+ str(cvDic['country'])+' from '+currentNation)
				
			return neuCV_list

		# read wiki table
		# wTxt=WT
		wikitable = open('WT-'+find_demonym(currentNation) + '.txt', 'r')
		wTxt = wikitable.read()
		wikitable.close()

		# use regex to find

		import re
		y = re.compile(r'[|] *?{{ *[fF][lL][aA][gG] *[|].*?}}[^}\\\|]*?\n[^}\\\|]*?[|][^}\\\|]*?{{.*?[|].*?}}')

		regX_found = y.findall(wTxt)
		cvList = list(regX_found)

		'''#print list of templates used in wikitable 
		cvList=list(set(regX_found))
		import pprint
		oFile = open('mod_list.py', 'w')
		oFile.write('x = ' + pprint.pformat(cvList) + '\n')
		oFile.close()
		'''
		
		# create list of dictionaries of country and template(visaReq)
		cvList = createCV_List(cvList)

		# hardcode to remove accents
		for i in range(len(cvList)):
			if 'voire' in cvList[i]['country']:
				cvList[i]['country'] = 'Ivory Coast'
			if 'ncipe' in cvList[i]['country']:
				cvList[i]['country'] = 'Sao Tome and Principe'

		'''
		import pprint
		oFile = open('VeeTmlts-'+currentNation+'.py', 'w')
		oFile.write('x = ' + pprint.pformat(cvList) + '\n')
		oFile.close()

		#get all visa templates
		vTypesFound=[]
		for i in range(len(cvList)):
			vTypesFound.append(cvList[i]['visaTemplate'])
		vTypesFound=list(set(vTypesFound))
		print('Visa templates found for '+currentNation)
		print(vTypesFound)
		'''

		logger('###log: number of countries found in wiki" for ' + currentNation + ' = ' + str(len(cvList)))

		score = getScore(cvList, currentNation)
		#convert to trillion
		score=score/1000000.0
		score = float("{0:.3f}".format(score))
		return score

	def gen_gdpAxsScore(self):
		WT=self.wiki2wText(self.__demonym)
		self.__gdpAxsScore = self.getTotGDP_Access(self.__name,WT)

	def createUrl(self):	#creates url for visa requirements
		self.__url='https://en.wikipedia.org/wiki/Visa_requirements_for_'+self.__demonym+'_citizens'

	def __init__(self, name):     #TODO: add population and pppcapita
		self.__name = name
		self.__demonym = find_demonym(name)
		self.__gdp = find_gdp(name)
		self.gen_gdpAxsScore()
		self.createUrl()
	
	def get_name(self):
		return self.__name
	
	def get_demonym(self):
		return self.__demonym

	def get_gdp(self):
		return self.__gdp
	
	def get_gdpAxsScore(self):
		return self.__gdpAxsScore
	
	def get_visaScoreList(self):
		return self.__visaScoreList

	def get_url(self):
		return self.__url

def makeAndDisplayFor(nation):
	
	x = country(nation)
	print('\nGDP Access Score for {} is {} Trillion USD'.format( x.get_name()  , x.get_gdpAxsScore()))
	print('More info: {} \n'.format( x.get_url()))
	return x

def loopThroughAllCountries():

	scoreSheet = []
	for i in range(len(cdList)):
		ctry = cdList[i]['country']
		aCountry = country(ctry)
		scoreSheet.append(aCountry)
	logger('###log: Score Sheet created.')
	
	scoreSheet=sorted(scoreSheet, key = lambda i: i.get_gdpAxsScore(),reverse=True)

	oFile = open('scoreList.py', 'w')
	oFile.write('#This is the final list of GDP Access Scores in Trillions of US dollars \n')
	oFile.write('z = [')
	for i in range(len(scoreSheet)-1):
		oFile.write('{ \'Country\': \''+scoreSheet[i].get_name()+'\', \'Score\': '+str(scoreSheet[i].get_gdpAxsScore())+' },\n')
	oFile.write('{ \'Country\': \''+scoreSheet[len(scoreSheet)-1].get_name()+'\', \'Score\': '+str(scoreSheet[len(scoreSheet)-1].get_gdpAxsScore())+' }]')
	oFile.close()
	logger('###log: scoreList.py generated')

	import csv
	#csvOutputFile = open('0_scoreSheet.csv', 'w', newline='')
	csvOutputFile = open('0_scoreSheet.csv', 'w')
	outputWriter = csv.writer(csvOutputFile)
	outputWriter.writerow([ 'Country' , 'Score in $T', 'GDP in $M' , 'Demonym' , 'Wikipedia Page'])
	outputWriter.writerow([ '' , '' ])
	
	for i in range(len(scoreSheet)):
		s=scoreSheet[i]
		outputWriter.writerow([ s.get_name(), s.get_gdpAxsScore(), s.get_gdp(), s.get_demonym(), s.get_url() ])
	csvOutputFile.close()
	print(' 0_scoreSheet.csv generated')

	return scoreSheet

def plotter():
	import matplotlib.pyplot as plt     
	import numpy as np
	try:
		import scoreList
	except ImportError:
		print('Error: Cannot import scoreList.py\nRun without arguments to generate it')
		raise SystemExit()
	t=scoreList.z

	countries=[]
	score=[]
	for i in range(10):
		countries.append(t[i]['Country'])
		score.append(float(t[i]['Score']))
	for i in range(len(t)-5,len(t)):
		countries.append(t[i]['Country'])
		score.append(float(t[i]['Score']))

	y_pos = np.arange(len(countries))

	plt.barh(y_pos, score, align='center', alpha=0.75,)
	plt.yticks(y_pos, countries)
	plt.xticks(rotation=0)
	plt.xlabel('GDP Access Score (More is Better)')
	plt.ylabel('Passports of')
	
	# Custom the subplot layout
	plt.subplots_adjust(left = 0.190)

	plt.xlim(20)
	plt.title('Bottom 5 and Top 10 Civilian Passports')
	
	plt.show()

##################### RUNNING MAIN


import sys
import os

logHuh=False
if len(sys.argv) > 1 and sys.argv[1]=='log' :
	logHuh=True
	logger('###log: logging')

refTable = getRefTable()

gTable = getGDPtable()

import a1_country_list
cdList = a1_country_list.countries


#work with arguments
if len(sys.argv) > 1:
	if sys.argv[1]=='list':
		listValidCountries()

	elif sys.argv[1]=='plot':
		plotter()

	elif sys.argv[1]=='show':
		PATH = './0_scoreSheet.csv'
		if not (os.path.isfile(PATH) and os.access(PATH, os.R_OK)):
			print('Error: CSV file not created yet\nRun with no arguments to generate it')
		else:
			os.system("xdg-open 0_scoreSheet.csv ")

	elif sys.argv[1]=='log':
		if len(sys.argv) > 2:
			nation=handleArgs(2)
			makeAndDisplayFor(nation)
		else:
			loopThroughAllCountries()	
	else:
		nation=handleArgs(1)
		makeAndDisplayFor(nation)	
else:
	loopThroughAllCountries()
