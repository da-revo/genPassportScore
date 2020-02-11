#creates template usage list
def getTableInfo(cList):
    tempDic={'country': 'cat', 'demonym': 'indo saram'}
    neuList = [ tempDic ]
    neuList.remove( tempDic )
    for i in range(len(cList)):
        a=cList[i]
        a=a[7:len(a)-2]
        a=workwithTemp(a)
        neuDic={'country': a, 'demonym': 'amerikaJinDesu'}
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

def mod(vList):
    nvList = []
    for i in range(len(vList)):
        a=vList[i]
        pos=-1
        for j in range(len(a)-3):
            if a[j:j+3]=='}\n|':
                pos=j+4
                break
        #x = re.compile(r'[{][{][f][l][a][g][|].*?[}][}]')
        a=a[pos:len(a)]
        nvList.append(a)
    return nvList


#read wiki table TODO: change filename to debug
wikitable = open('wikitable.txt', 'r')
table=wikitable.read()
wikitable.close()
#print(table)

#use regex to find 
import re
x = re.compile(r'[{][{][f][l][a][g][|].*?[}][}]')
y = re.compile(r'[{][{][f][l][a][g][|].*?[}][}]\s*[|]\s*[{][{].*?[|].*?[}][}]')


cList = x.findall(table)
vList = y.findall(table)
#print(vList)
vList=mod(vList)
vList=list(set(vList))

#write list of mod
import pprint
oFile = open('D_templateUsageList.py', 'w')
oFile.write('\n x = ' + pprint.pformat(vList) + '\n')
oFile.close()

print(' The template usage list has been generated ')
#countries=getTableInfo(cList)
