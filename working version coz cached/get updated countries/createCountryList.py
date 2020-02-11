def findInnerCountries(wList):
    tempDic={'country': 'cat', 'demonym': 'indo saram'}
    neuList = [ tempDic ]
    neuList.remove( tempDic )
    for i in range(len(wList)):
        a=wList[i]
        a=a[7:len(a)-2]
        a=workwithTemp(a)
        neuDic={'country': a, 'demonym': 'amerikaJinDesu'}
        neuList.append(neuDic)
    #hard code Japan as we start from there 
    neuDic={'country': 'Japan', 'demonym': 'amerikaJinDesu'}
    neuList.append(neuDic)
    #print(neuList)
    return neuList

def workwithTemp(temp):
    flag=False
    for i in range(len(temp)):
        if temp[i]=="|":
            if temp[i+1]=='s':
                neutemp=temp[0:i]
                flag=True
            if temp[i+1]=='n':
                neutemp=temp[i+6:len(temp)]
                flag=True
    if flag==False:
        neutemp=temp
    return neutemp



#read wiki table
wikitable = open('wikitable.txt', 'r')
table=wikitable.read()
wikitable.close()
#print(table)

#use regex to find 
import re
x = re.compile(r'{{[Ff]lag[|].*?}}')

wList = x.findall(table)
#if y is None:
#    print("\nerror: no match\n")

#change names with accents
for i in range(len(wList)):
    if 'voire' in wList[i]:
        wList[i]='Ivory Coast'
    if 'ncipe' in wList[i]:
        wList[i]='Sao Tome and Principe'

countries=findInnerCountries(wList)
import pprint
pprint.pformat(countries)

#write to country_list
c_list = open('country_list_0.py', 'w')
c_list.write('#TODO: replace amerikaJinDesu with appropriate name for citizens of the country (according to wikipedia)')
c_list.write('\n#reference: https://en.wikipedia.org/wiki/Category:Visa_requirements_by_nationality ')
c_list.write('\n\ncountries = ' + pprint.pformat(countries) + '\n')
c_list.close()

import country_list_0
print(country_list_0.countries)

import fillsomepeopleinfo