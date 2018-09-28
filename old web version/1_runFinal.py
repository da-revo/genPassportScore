
def getRefTable():

    try:
        import a_weightsTable
    
    except ImportError:
        print('###log : could not import a_weightsTable.py ; Using hardcoded weights ')
        nTable=[
        {'weight': '1.0' , 'templates': ['free' ] , 'desc': 'Freedom of Movement' },
        {'weight': '0.9' , 'templates': ['yes'] , 'desc': 'Visa Free' },
        {'weight': '0.7' , 'templates': ['Optional' , 'yes-no']  , 'desc': 'Visa on Arrival' },
        {'weight': '0.5' , 'templates': [ 'yes2' ] , 'desc': 'eVisa' },
        {'weight': '0.4' , 'templates': [ 'no' ,'n/a'] , 'desc': 'Visa required' },
        {'weight': '0.0' , 'templates': [ 'black', 'BLACK' ] , 'desc': 'Banned' },
        ]
    
    else:
        nTable=a_weightsTable.refTable

    return nTable

def get_demonym(country):
    #return demonym and return countryName 

    flag=False
    for i in range(len(cdList)):
        #Returns the first country which matches the query as a substring.
        if country in cdList[i]['country']:
            flag=True
            return cdList[i]
    if flag==False:
        print('country & demonym not found in country_list')

def getreply(payload):
        url = 'https://en.wikipedia.org/w/api.php?'
        #get stuff from url while injecting payload
        import requests
        #import json
        r = requests.get(url=url, params=payload)
        #jData = json.loads(r.content)
        jData = r.json()
        return(jData)

def getGDPtable():
    ###get info from wikipedia , get wikitext from that , creates the GDPtable and returns it

    payload = {
	"action": "query",
	"format": "json",
	"prop": "revisions",
	"titles": "List_of_countries_by_GDP_(nominal)",
	"rvprop": "content",
	"rvlimit": "1",
	"rvsection": "1"
    }
    jData=getreply(payload)

    import a_peeFormatFs

    #go inside the nest
    jData=jData['query']
    jData=jData['pages']
    pageNo=list(jData)[0]
    jData=jData[pageNo]
    jData=jData['revisions']

    contents=(str)(jData[0])
    contents=a_peeFormatFs.unbrace(contents)
    
    ### make a list of all the countries and their GDPs (newest available)

    #use regex to find 
    import re
    x = re.compile(r'{{[fF]lag\|.*?}}.*?\|\|.*?[\|]{1}?.*?[\|]{1}?[\-}]{1}?', re.DOTALL)

    gdpDATA = x.findall(contents)
    del contents

    GDPtable=[]
    for i in range(len(gdpDATA)):
        t=gdpDATA[i]
        #snip tail text
        t=(t[0:len(t)-4])
        #find country
        y = re.compile(r'{{[fF]lag\|.*?}}')
        theCountry=y.findall(t)[0]
        theCountry=theCountry[7:len(theCountry)-2]
        
        #replace accented names with a unique substring without accents to match  
        if 'voire' in theCountry:
            theCountry='Ivory Coast'
        if 'ncipe' in theCountry:
            theCountry='Sao Tome and Principe'

        #find gdp
        y = re.compile(r'{{nts\|.*?}}')
        p=y.findall(t)
        theGDP=''
        if len(p) <=0 :
            j=len(t)-1
            while j>=0:
                if t[j] == '|':
                    theGDP=t[j+1:len(t)]
                    break
                j=j-1
        else :
            theGDP=p[0]
            theGDP=theGDP[6:len(theGDP)-2]
        #remove commas from theGDP and convert to integer
        theGDP= float(''.join(i for i in theGDP if  i.isdigit()))
        theGDP = float("{0:.2f}".format(theGDP))  
        
        aDic= {'Country': theCountry , 'GDP' : theGDP}
        GDPtable.append(aDic)  

    #write gdp table to file
    import pprint
    c_list = open('GDPtable.py', 'w')
    c_list.write('#uses the first gdp that matches the country \n')
    c_list.write('#Ivory Coast and Sao Tome and Principe may have been de accented \n')
    c_list.write('GDPtable = '+pprint.pformat(GDPtable))
    c_list.close()
    print('###log: created GDPtable.py ')
    return(GDPtable)

def wiki2wText(nationality):
    #get info from wikipedia and returns wikitext

    #TODO: convert white spaces to _ underscore

    #find rvsection
    payload = {
	"action": "parse",
	"format": "json",
	"prop": "sections",
	"page": 'Visa_requirements_for_'+nationality+'_citizens'
    }
    t=getreply(payload)
    
    t=t['parse']
    sections=t['sections']
    
    f=False
    for i in range(len(sections)):
        #print(sections[i]['anchor']+' is anchor at index '+i+' for '+nationality)
        if sections[i]['anchor'].lower()=='visa_requirements':
            rvsection=sections[i]['number']
            f=True
            break
    if f==False :
        print('###log: visa_requirements section not found in wiki page for '+nationality)
    
    section=str(rvsection)
    print('###log: rvsecion for '+nationality+' is '+section)

    payload = {
	"action": "query",
	"format": "json",
	"prop": "revisions",
	"titles": 'Visa_requirements_for_'+nationality+'_citizens',
	"rvprop": "content",
	"rvlimit": "1",
	"rvsection": rvsection
    }
    jData=getreply(payload)

    import a_peeFormatFs

    #go inside the nest
    jData=jData['query']
    jData=jData['pages']
    pageNo=list(jData)[0]
    jData=jData[pageNo]
    jData=jData['revisions']

    contents=(str)(jData[0])
    #contents=a_peeFormatFs.unbrace(a_peeFormatFs.unbrace(contents))

    #write to file with prettiness
    a_peeFormatFs.ppWrite(contents,nationality+'-WT')
    print('###log: got api Data / wikiTable for the '+nationality+' citizens ')
    return contents

def getTotGDP_Access(currentNation,WT):
    ###gets visa score for the country

    def getScore(cvList,currentNation):

        def findWeight(level):
        
            flag=False
            for i in range(len(refTable)):
                found=False
                for j in range(len(refTable[i]['templates'])):
                    if level.lower()==refTable[i]['templates'][j].lower():
                        found=True
                        break
                if found:
                    return float("{0:.2f}".format((float(refTable[i]['weight']))))
            if flag==False:
                print('error: template not found in refTable. template was '+level)
                return(0)

        

        ###create list of dictionaries and find final score
        GDP_AccessList=[]
        tDic={}
        total_GDP_Access=0
        #find for currentNation
        found=0
        for j in range(len(gTable)):

            if (currentNation in gTable[j]['Country']) or (gTable[j]['Country'] in currentNation):
                tsuff=gTable[j]['GDP']*findWeight('free')
                tDic={'Country': currentNation, 'VisaRequired': 'free' , 'GDP_Access': float("{0:.2f}".format(tsuff)) }
                GDP_AccessList.append(tDic)
                total_GDP_Access=total_GDP_Access+gTable[j]['GDP']
                found=1
                break
                
        if found==0:
            print('GDP_Access not found for'+currentNation+' to itself')
        
        #now the rest of the countries
        for i in range(len(cvList)):
            found=0
            for j in range(len(gTable)):
                
                if (cvList[i]['country'] in gTable[j]['Country']) or (gTable[j]['Country'] in cvList[i]['country']):
                    tsuff=gTable[j]['GDP']*findWeight(cvList[i]['visaTemplate'])
                    tsuff=float("{0:.2f}".format(tsuff))
                    #print(' a*b=c ',(gTable[j]['GDP'],findWeight(cvList[i]['visaTemplate'], tsuff))
                    tDic={'Country': cvList[i]['country'], 'VisaRequired': cvList[i]['visaTemplate'] ,'GDP_Access': tsuff }
                    GDP_AccessList.append(tDic)
                    total_GDP_Access=total_GDP_Access+tsuff
                    found=1
                    break
            if found==0:
                print('###log: GDP_Access not found for '+currentNation+' to '+cvList[i]['country'])
        
        
        import pprint
        c_list = open(get_demonym(currentNation)['demonym']+'GdpAxs.py', 'w')
        c_list.write('#GDP Access List for'+currentNation+' \n')
        c_list.write('GDPtable = '+pprint.pformat(GDP_AccessList))
        c_list.close()
        print('###log: created '+currentNation+'GdpAxs.py ')
        return total_GDP_Access

    def createCV_List(cvList):
        #create list of dictionaries of country and template(visaReq)
        neuCV_list=[]
        cvDic={}

        
        for i in range(len(cvList)):

            ###find Country
            x = re.compile(r'{{ *[fF][lL][aA][gG] *[|].*?}}')
            c=x.findall(cvList[i])[0]
            #find name
            x = re.compile(r'name=.*?}')
            if len(x.findall(c))!=0:
                c=x.findall(c)[0]
                c=c[5:-1]
            else:
                #remove state
                x = re.compile(r'lag\|[^}]*?\|')
                if len(x.findall(c))!=0:
                    c=x.findall(c)[0]
                    c=c[4:-1]
                else:
                    #find regularly
                    x = re.compile(r'lag\|[^}]*?}')
                    c=x.findall(c)[0]
                    c=c[4:-1]

            ###find visa template
            beginer=0
            ender=0
            saveEnd=False
            for j in range( 2 , len(cvList[i])-2 ) :
                if cvList[i][j]=='{' and cvList[i][j+1]=='{':
                    beginer=j+2
                    #print('found { {')
                    saveEnd=True
                elif cvList[i][j]=='|' and saveEnd==True:
                    ender=j
                    #print('found | ')
                    break
            
            v=cvList[i][beginer:ender]

            cvDic={'country': c , 'visaTemplate': v }
            neuCV_list.append(cvDic)

        return neuCV_list

    #read wiki table
    #wTxt=WT
    wikitable = open(get_demonym(currentNation)['demonym']+'-WT.txt', 'r')
    wTxt=wikitable.read()
    wikitable.close()
    
    #use regex to find 

    import re
    y = re.compile(r'{{ *[fF][lL][aA][gG] *[|].*?}}[^}\\\|]*?\n[^}\\\|]*?[|][^}\\\|]*?{{.*?[|].*?}}')

    regX_found = y.findall(wTxt)
    cvList=list(regX_found)

    '''#print list of templates used in wikitable 
    cvList=list(set(regX_found))
    import pprint
    oFile = open('mod_list.py', 'w')
    oFile.write('x = ' + pprint.pformat(cvList) + '\n')
    oFile.close()
    '''

    #create list of dictionaries of country and template(visaReq)
    cvList=createCV_List(cvList)

    #hardcode to remove accents
    for i in range(len(cvList)):
        if 'voire' in cvList[i]['country']:
            cvList[i]['country']='Ivory Coast'
        if 'ncipe' in cvList[i]['country']:
            cvList[i]['country']='Sao Tome and Principe'

    import pprint
    oFile = open(currentNation+'VeeTmlts.py', 'w')
    oFile.write('x = ' + pprint.pformat(cvList) + '\n')
    oFile.close()
    
    print('###log: number of countries found in the wikipedia section \"visa_requirements\" for '+currentNation+' = '+str(len(cvList))+'\n')

    '''#get all visa templates
    vTypesFound=[]
    for i in range(len(cvList)):
        vTypesFound.append(cvList[i]['visaTemplate'])
    vTypesFound=list(set(vTypesFound))
    print('Visa templates found for '+currentNation)
    print(vTypesFound)
    '''

    score=getScore(cvList,currentNation)
    return score
    # print('GDP Access Score for '+currentNation+' is '+str(score))

    

#def loopThrouhAllCountries():
    #find scores of all countries and return in a list of dictionaries

######################### RUNNING MAIN

import sys
from flask import Flask, request, render_template
refTable=getRefTable()
gTable=getGDPtable()
import a_country_list
cdList=a_country_list.countries

app = Flask(__name__)

@app.route('/')
def index():
    stat = "display:none"
    return render_template('index.html', status = stat)

@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'POST':

        nation = request.form['country']

        #TODO: test all countries


        #output fo argument
        # nation='Japan'
        # f=nation
        # if(len(sys.argv) != 1):
        #     f=''
        #     for i in range(1, len(sys.argv)):
        #         f = f + sys.argv[i] + ' '
        # nation=f.strip()

        nationality=get_demonym(nation)['demonym']
        country = get_demonym(nation)['country']

        #TODO: make it work without writing and also offline
        WT=wiki2wText(nationality)

        score = getTotGDP_Access(nation,WT)
        stat = "display:block"
        return render_template('index.html', country = country, totGdp = score/1000000.0, status = stat)

if __name__ == "__main__":
    app.run()
