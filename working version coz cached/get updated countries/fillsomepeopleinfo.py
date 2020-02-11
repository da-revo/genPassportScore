wrt = open('wikipedia_people.txt', 'r')
wikipeople=wrt.read()

import country_list_0 as cList 
lst=cList.countries

#start write
c_list = open('country_list.py', 'w')
c_list.write('#TODO: replace amerikaJinDesu with appropriate name for citizens of the country (according to wikipedia)')
c_list.write('\n#reference: https://en.wikipedia.org/wiki/Category:Visa_requirements_by_nationality ')


#go through list of countries
for i in range(len(lst)):
    if (lst[i]['demonym']=='amerikaJinDesu'):
        t=lst[i]['country']

        suffix=['','n','i','ian','an','nian','ese']
        for k in suffix:
            t1=t+k
            
            #check if it exists in wikipeople
            found=False
            for j in range(20,len(wikipeople)-len(t)):
                if wikipeople[j:j+len(t1)]==t1:
                    found=True
                    break
            if found==True:
                print(t1)
                lst[i]['demonym']=t1
        

import pprint
pprint.pformat(lst)
c_list.write('\n\ncountries = ' + pprint.pformat(lst) + '\n')
c_list.close()
