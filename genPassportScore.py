'''
###TODO:
plot on map
compare with regular passport rankings
make it not read any file
find to taiwan

'''

def logger(text):
	if logHuh == True:
		print(text)

def workWithLog(argz):
	logHuh=False
	nArgz=[]
	if len(argz) > 1 and argz[1]=='log' :
		logHuh=True
		logger('###log: logging')
		nArgz.append(argz[0])
		for i in range(2, len(argz)):
			nArgz.append(argz[i])
		return nArgz
	if logHuh==False:
		return False

def ppWrite(contents,filename):
    #write to file with prettiness
    wrt = open('./wikitext/'+filename+'.txt', 'w')
    i=0
    while i < len(contents):
        letter = contents[i]
        if letter=="\\":
            i=i+1
            if contents[i]=="n":
                wrt.write("\n")
            else:
                wrt.write(letter)
        else:
            wrt.write(letter)
        i = i + 1
    wrt.close()

def checkValidCountry(nation):
	logger("###log: checking validity of "+nation)
	nation=nation.strip()
	nation=nation.replace('-', ' ')
	nation=nation.replace('_', ' ')
	nation=nation.lower()
	nation=nation.title()
	
	if nation == 'Usa' or nation == 'Us':
		nation='United States'
	if nation == 'Uae':
		nation='United Arab Emirates'
	if nation == 'Uk':
		nation='United Kingdom'
	#check if it exists
	exists=False
	for i in range(len(cdList)):
		if nation.lower() == cdList[i]['country'].lower():
			exists=True
	if exists==False and webhuh!=True:
		print('Error: Invalid country name, '+nation+' entered ')
		print('enter \"list\" as argument to see all valid countries')
		raise SystemExit()
	if exists==False and webhuh==True:
		logger('###log: checked validity of '+nation+'. it is not valid')
		return False
	return nation

def handleArgs(st):
	f=''
	for i in range(st, len(argz)):
		f = f + argz[i] + ' '
	nation=f.strip()
	nation=checkValidCountry(nation)
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
		import a2_weightsTable
		logger('###log: imported a2_weightsTable.py')
	except ImportError:
		logger('###log: could not import a2_weightsTable.py ; Using hardcoded weights ')
		nTable = [
			{'weight': 1.0, 'templates': ['free'], 'desc': 'Freedom of Movement'},
			{'weight': 0.9, 'templates': ['yes','yes '], 'desc': 'Visa not Required'},
			{'weight': 0.7, 'templates': ['Optional', 'yes-no'], 'desc': 'Visa on Arrival'},
			{'weight': 0.5, 'templates': ['yes2'], 'desc': 'Electronic Visa'},
			{'weight': 0.4, 'templates': ['no','no ', 'n/a'], 'desc': 'Visa is required'},
			{'weight': 0.0, 'templates': ['black', 'BLACK'], 'desc': 'Travel not Allowed'},
		]
		# write weights table to file
		import pprint
		c_list = open('a2_weightsTable.py', 'w')
		c_list.write('refTable = ' + pprint.pformat(nTable))
		c_list.close()
		logger('###log: created a2_weightsTable.py ')
	else:
		nTable = a2_weightsTable.refTable

	return nTable

def find_demonym(nation):

	flag = False
	for i in range(len(cdList)):
		if cdList[i]['country'].lower() == nation.lower():
			flag = True
			return cdList[i]['demonym']
	if flag == False:
		print('nation & demonym of '+nation+' not found in country_list')

def getGDPtable():	#get info from wikipedia , get wikitext from that , creates the GDPtable and returns it

	try:
		import a3_GDPtable
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

		# go inside the nest
		jData = jData['query']
		jData = jData['pages']
		pageNo = list(jData)[0]
		jData = jData[pageNo]
		jData = jData['revisions']

		contents = (str)(jData[0])

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
		c_list = open('a3_GDPtable.py', 'w')
		c_list.write('#uses the first gdp that matches the country \n')
		c_list.write('#Ivory Coast, Sao Tome and Principe and Curacao may have been de accented \n')
		c_list.write('GDPtable = ' + pprint.pformat(GDPtable))
		c_list.close()
		logger('###log: created a3_GDPtable.py ')
		
	else:
		GDPtable = a3_GDPtable.GDPtable
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
	__rank = False
	__gdp  = 0
	#__pppCapita = 0
	#__population = 0
	__gdpAxsScore = 0.0
	__visaScoreList = []    #stores dictionaries with keys, country and visaScore 
	__demonym = ''
	__url = ''

	def createUrl(self):	#creates url for visa requirements
		self.__url='https://en.wikipedia.org/wiki/Visa_requirements_for_'+self.__demonym+'_citizens'
		if self.__demonym=='Monegasque':
			self.__url='https://en.wikipedia.org/wiki/Visa_requirements_for_Mon%c3%a9gasque_citizens'
				
	def wiki2wText(self,nationality):
		# get info from wikipedia and returns wikitext

		# check if wikitext exists
		PATH = './wikitext/WT-' + nationality + '.txt'

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
			if self.__demonym=='Monegasque':
				payload['page']='Visa_requirements_for_Mon\u00E9gasque_citizens'
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
			if self.__demonym=='Monegasque':
				payload['titles']='Visa_requirements_for_Mon\u00E9gasque_citizens'
			jData = getreply(payload)

			# go inside the nest
			jData = jData['query']
			jData = jData['pages']
			pageNo = list(jData)[0]
			jData = jData[pageNo]
			jData = jData['revisions']

			contents = (str)(jData[0])

			# write to file with prettiness
			ppWrite(contents, 'WT-'+nationality )
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

			def findDesc(level):

				flag = False
				for i in range(len(refTable)):
					found = False
					for j in range(len(refTable[i]['templates'])):
						if level.lower() == refTable[i]['templates'][j].lower():
							found = True
							break
					if found:
						return refTable[i]['desc']
				if flag == False:
					logger('###error: template not found in refTable. template was ' + level)
					return ('n/a')	

			GDP_AccessList = []
			tDic = {}
			total_GDP_Access = 0
			# find for currentNation
			found = 0
			for j in range(len(gTable)):

				if (currentNation in gTable[j]['Country']) or (gTable[j]['Country'] in currentNation):
					tsuff = gTable[j]['GDP'] * findWeight('free')
					tDic = {'Country': currentNation, 'VisaTemplate': 'free',
							'GDP_Access': float("{0:.3f}".format(tsuff)), 'VisaRequirement': 'Freedom of Movement'}
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
						tDic = {'Country': cvList[i]['country'], 'VisaTemplate': cvList[i]['visaTemplate'],
								'GDP_Access': tsuff , 'VisaRequirement': findDesc(cvList[i]['visaTemplate'])}
						GDP_AccessList.append(tDic)
						total_GDP_Access = total_GDP_Access + tsuff
						found = 1
						break
				if found == 0:
					logger('###log: no GDP_Access for ' + currentNation + ' to ' + cvList[i]['country'])

			import pprint
			c_list = open('./GDP_Access/GdpAxs'+find_demonym(currentNation) + '.py', 'w')
			c_list.write('#GDP Access List for' + currentNation + ' \n')
			c_list.write('GDPtable = ' + pprint.pformat(GDP_AccessList))
			c_list.close()
			logger('###log: created GdpAxs' + currentNation + '.py ')
			GDP_AccessList=sorted(GDP_AccessList, key = lambda i: i['GDP_Access'],reverse=True)
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
		wikitable = open('./wikitext/WT-'+find_demonym(currentNation) + '.txt', 'r')
		wTxt = wikitable.read()
		wikitable.close()

		# use regex to find

		import re
		y = re.compile(r'[|] *?{{ *[fF][lL][aA][gG] *[|].*?}}[^}\\\|]*?\n[^}\\\|]*?[|][^}\\\|]*?{{.*?[|].*?}}')

		regX_found = y.findall(wTxt)
		cvList = list(regX_found)
		
		# create list of dictionaries of country and template(visaReq)
		cvList = createCV_List(cvList)

		# hardcode to remove accents
		for i in range(len(cvList)):
			if 'voire' in cvList[i]['country']:
				cvList[i]['country'] = 'Ivory Coast'
			if 'ncipe' in cvList[i]['country']:
				cvList[i]['country'] = 'Sao Tome and Principe'

		logger('###log: number of countries found in wiki" for ' + currentNation + ' = ' + str(len(cvList)))

		score = getScore(cvList, currentNation)
		#convert to trillion
		score=score/1000000.0
		score = float("{0:.3f}".format(score))
		return score

	def gen_gdpAxsScore(self):
		WT=self.wiki2wText(self.__demonym)
		self.__gdpAxsScore = self.getTotGDP_Access(self.__name,WT)

	def gen_Rank(self,scoreList):
		count=1
		for i in range(len(scoreList.z)):
			if scoreList.z[i]['Score'] > self.__gdpAxsScore:
				count+=1
		self.__rank=count
		return self.get_Rank()

	def __init__(self, name):     #TODO: add population and pppcapita
		
		self.__name = name
		self.__demonym = find_demonym(name)
		self.createUrl()
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
	
	def get_Rank(self):
		return self.__rank

def makeAndDisplayFor(nation):
	
	x = country(nation)
	print('\n{}'.format( x.get_url()))
	print('\nGDP Access Score for {} is {} Trillion USD'.format( x.get_name()  , x.get_gdpAxsScore()))
	if scoreListExists==True:
		print('Rank is {} out of {} countries\n'.format(x.gen_Rank(scoreList),len(scoreList.z)))
	
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

	import scoreList

	import csv
	#csvOutputFile = open('0_scoreSheet.csv', 'w', newline='')
	csvOutputFile = open('0_scoreSheet.csv', 'w')
	outputWriter = csv.writer(csvOutputFile)
	outputWriter.writerow([ 'Country' , 'Score in $T', 'Rank' , 'GDP in $M' , 'Demonym' , 'Wikipedia Page'])
	outputWriter.writerow([ '' , '' ])
	
	for i in range(len(scoreSheet)):
		s=scoreSheet[i]
		outputWriter.writerow([ s.get_name(), s.get_gdpAxsScore(), s.gen_Rank(scoreList), s.get_gdp(), s.get_demonym(), s.get_url() ])
	csvOutputFile.close()
	print(' 0_scoreSheet.csv generated')

	return scoreSheet

def plotter(pltArgs,createhuh=False):		#if pltArgs is None then just display top mid bottom
	import matplotlib.pyplot as plt     
	import numpy as np
	if scoreListExists==False:
		print('###log: Cannot import scoreList.py generating it')
		loopThroughAllCountries()
		if scoreListExists==False:
			print('Error: Cannot import scoreList.py')
			raise SystemExit()
	sList=scoreList.z

	countries=[]
	score=[]
	
	def appendr(i):
		countries.append(sList[i]['Country'])
		score.append(float(sList[i]['Score']))
		if len(sList[i]['Country'])>13:
			return True
		else:
			return False

	name2Long=False

	if pltArgs == None:
		logger("###log: getting top, middle and bottom to plot")
		for i in range(7):
			name2Long+=appendr(i)
		i=int(len(sList)/2)
		for i in range(i-1,i+2):
			name2Long+=appendr(i)
		for i in range(len(sList)-5,len(sList)):
			name2Long+=appendr(i)
		
	else:
		logger("###log: getting listed countries to plot")
		conts=[]
		#convert list to a useable string
		sArgs=','
		for i in range(len(pltArgs)):
			sArgs+=pltArgs[i]+' '
		sArgs+=','
		#print(sArgs)
		#extract countries from list
		commaPos=0
		for i in range(1,len(sArgs)):
			if sArgs[i]==',':
				j=commaPos+1
				tCon=''
				while sArgs[j]!=',':
					tCon+=sArgs[j]
					j+=1
				tCon=checkValidCountry(tCon)
				if tCon!= False:
					logger('###log: found '+tCon+' in pltArgs')
					conts.append(tCon)
				commaPos=j
		#find info to plot
		for kont in conts:
			for k in range(len(sList)):
				if sList[k]['Country']==kont:
					name2Long+=appendr(k)

	y_pos = np.arange(len(countries))

	plt.barh(y_pos, score, align='center', alpha=0.75,)
	plt.yticks(y_pos, countries)
	plt.xticks(rotation=0)
	plt.xlabel('GDP Access Score in Trillions of US Dollars')
	plt.ylabel('Civilian Passports of ')
	

	plt.xlim(20)
	if pltArgs == None:
		plt.title('Bottom 5, Middle 3 and Top 7 Civilian Passports')

	if not name2Long:
		plt.subplots_adjust(left = 0.210)
	else:
		plt.subplots_adjust(left = 0.320)

	if webhuh==False:
		PATH='./0_plot.png'
		if not (os.path.isfile(PATH) and os.access(PATH, os.R_OK)):
			plt.savefig(PATH)
		logger('###log: created 0_plot.png')
		plt.show()
		return
	else:
		#create for web version
		if createhuh==True:
			PATH='./static/images/0_plot.png'
			if not (os.path.isfile(PATH) and os.access(PATH, os.R_OK)):
				plt.savefig(PATH)
			logger('###log: created /static/images/0_plot.png')
		else:
			import random
			locAndFile='./static/images/plot/last_plot_'+str(random.randint(000000, 999999))+'.png'
			plt.savefig(locAndFile)
			plt.close('all')
			logger('###log: saved plot to '+locAndFile)
			return locAndFile

def compare( argee ):

	logger('###log: comparing')
	print(argee)
	# remove this part if logic needs to change
	if 'plot' in argz :
		argz.remove('plot')
	if 'show' in argz :
		argz.remove('show')

	p=''
	q=''
	pos=-1

	for i in range(len(argee)):
		if argee[i]=='vs':
			pos=i

	for i in range(1,pos):
		p+=argee[i]+' '
	p=p[0: len(p)-1]
	p=checkValidCountry(p)

	for i in range(pos+1,len(argee)):
		q+=argee[i]+' '
	q=q[0: len(q)-1]
	q=checkValidCountry(q)

	# display error in web ver
	if (q==None or p==None) and webhuh==True:
		return None

	a = country( p )
	b = country( q )

	if a.get_gdpAxsScore() < b.get_gdpAxsScore():
		a,b = b,a
		p,q = q,p

	difL=[]

	avL=a.get_visaScoreList()
	bvL=b.get_visaScoreList()
	
	#fill the difference list,  difL
	for i in range( len( avL ) ) :
		for j in range( len(bvL) ):
			if avL[i]['Country'].lower() == bvL[j]['Country'].lower() :
				if avL[i]['VisaRequirement'] != bvL[j]['VisaRequirement'] :
					difL.append( { 'Country': avL[i]['Country'] ,
									'GDP_Access_Difference': float("{0:.3f}".format(avL[i]['GDP_Access']-bvL[j]['GDP_Access'])),
								'aVisaRequirement': avL[i]['VisaRequirement'] ,'bVisaRequirement': bvL[j]['VisaRequirement'] } )

	difL=sorted(difL, key = lambda i: abs(i['GDP_Access_Difference']),reverse=True)
	logger('###log: sorted difference list, difL')

	## output result
	if webhuh==True:
		if scoreListExists==False:
			logger('###log: ScoreList does not exist. creating...')
			loopThroughAllCountries()
		return difL,a.get_gdpAxsScore(),a.gen_Rank(scoreList),a.get_name(),b.get_name(), b.gen_Rank(scoreList), b.get_gdpAxsScore()
	#print the list
	print('\nHere is the list of differences ordered in ascending order of the magnitude of the difference\n')
	print('The + and - signs identify the countries that are easier to access from the assigned country\n')
	for i in range( len(difL)-1, -1, -1):	
		dMsg=''
		if difL[i]['GDP_Access_Difference'] > 0:
			dMsg='+ '
		else:
			dMsg='- '
		dMsg=dMsg+difL[i]['Country']+' : '
		if	len(difL[i]['Country'])+5 < 8*4:
			dMsg=dMsg+'\t'
		if	len(difL[i]['Country'])+5 < 8*3 :
			dMsg=dMsg+'\t'
		if	len(difL[i]['Country'])+5 < 8*2:
			dMsg=dMsg+'\t'
		
		dMsg=dMsg+'\t {} \t vs \t {}'.format(difL[i]['aVisaRequirement'],difL[i]['bVisaRequirement'])
		print(dMsg)

	if scoreListExists==False:
		print('\n\t(+) {} = {}    vs    {} = {} (-)\n'.format( p , a.get_gdpAxsScore(),
				b.get_gdpAxsScore(), q ))
	else:
		print('\n\t(+) {} = {}  [#{}]    vs    [#{}]  {} = {} (-)\n'.format( p , a.get_gdpAxsScore(),
				a.gen_Rank(scoreList), b.gen_Rank(scoreList), b.get_gdpAxsScore(), q ))
		
def helpr():
	print(
		"\n *You can modify the weights in the a2_weightsTable.py and the program"
		+"\n  ....will use those weights ; else it will use the hardcoded weights\n"
		+"\n *\"a2_weightsTable.py\" is generated after the first run\n"
		+"\n *The ranks will be displayed after first execution without arguments\n"
		+"\n\n==> Here's the list of arguments you can use...\n\n"
		+"\n-> `<country>` to find GDP access score for the country input as country\n"
		+"\n-> `<country1> vs <country2>` to get a detailed comparison of the access each"
		+"\n    ....of the two passports grants ordered by the magnitude of difference\n"
		+"\n-> `all` to generate a CSV file with all scores\n"
		+"\n-> `list` to get a list of valid countries\n"
		+"\n-> `show` to open up the created csv file\n"
		+"\n-> `plot` to plot countries on a bar graph\n"
		+"\n-> `log` before any other argument to get all actions performed, output"
		+"\n    ....to the terminal\n"
		+"\n"
		)

############# WEB VERSION

def webbie():
	from flask import Flask, request, render_template
	app=Flask(__name__)

	def refreshPlotFolder():
		nuPath="./static/images/plot/"
		if os.path.isdir(nuPath):
			import shutil
			shutil.rmtree(nuPath)
		os.makedirs(nuPath)

	@app.route('/')
	def index():
		return render_template("index.html")
	
	@app.route('/country/<countree>')
	def test(countree):
		x = country(checkValidCountry(countree))
		return render_template("country.html",
				cName=x.get_name(), cScore=x.get_gdpAxsScore() , cURL=x.get_url(),
				cvList=x.get_visaScoreList() )
	
	@app.route('/compare/<c1>-vs-<c2>')
	def compareW(c1,c2):
		
		print(c1,c2)
		s='blah '+c1+' vs '+c2
		ag=s.split()
		logger('###log: argument from url is '+str(ag))
		difL, aS,aR,aN,bN,bR,bS =compare(s.split())
		if difL==None:
			return 'Fatal Error: at least one country is invalid'
		
		return render_template("compare.html",rank1=aR,country1=aN,score1=aS,
								difL=difL, rank2=bR,country2=bN,score2=bS)
		
	@app.route('/plot', methods = ['POST', 'GET'])
	def plotCustom():
		if request.method == 'POST':
			arg=[]
			for i in range(3):
				arg.append(request.form['country'+str(i)]+',')
			refreshPlotFolder()
			url=plotter(pltArgs=arg)
			return render_template("plot.html", url =url, shw='block')
		elif request.method == 'GET':
			refreshPlotFolder()
			url=plotter(pltArgs=['chigoo,', 'united states,', 'germany'])	#TODO make work
			return render_template("plot.html", url =url, shw='none')
	
	@app.route('/plot/top')
	def plotTop():
		PATH='./static/images/0_plot.png'
		if not (os.path.isfile(PATH) and os.access(PATH, os.R_OK)):
			logger('###log: no file at ./static/images/0_plot.png ; creating... ')
			plotter(None,True)
		return render_template("top.html", url ='/static/images/0_plot.png')
		
	app.run()

##################### RUNNING MAIN


import sys
import os
if not os.path.isdir('./wikitext/'):
	os.makedirs('./wikitext/')
if not os.path.isdir('./GDP_Access/'):
	os.makedirs('./GDP_Access/')


argz=sys.argv

logHuh=False
if workWithLog(argz)!=False:
	argz=workWithLog(argz)
	logHuh=True
webhuh=False

scoreListExists=False
try:
	import scoreList
except ImportError:
	logger('###log: scoreList does not exist')
else:	
	scoreListExists=True

refTable = getRefTable()

gTable = getGDPtable()

import a1_country_list
cdList = a1_country_list.countries

#work with arguments
if len(argz) > 1:
	
	if argz[1]=='list':
		listValidCountries()

	elif argz[1]=='web':
		webhuh=True
		webbie()

	elif argz[1]=='plot':
		try:
			if argz[2]=='top':
				plotter(pltArgs=None)
			else:
				plotter(pltArgs=argz[2:])
		except IndexError:
				print('\n no arguments provided for plot ')
				print(' use `top` after plot to get the top 7, bottom 5 and middle 3')
				print(' or list countries with `,`\n')

	elif argz[1]=='all':
		loopThroughAllCountries()

	
	elif argz[1]=='show':
		PATH = './0_scoreSheet.csv'
		if not (os.path.isfile(PATH) and os.access(PATH, os.R_OK)):
			print('Error: CSV file not created yet\nRun with no arguments to generate it')
		else:
			os.system("xdg-open 0_scoreSheet.csv")
	
	elif 'vs' in argz :
			compare(argz)
	
	else:
		nation=handleArgs(1)
		makeAndDisplayFor(nation)	
else:
	helpr()
	