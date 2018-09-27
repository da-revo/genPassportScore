#functions for formatting


def unbrace(contents):
    #function takes text and returns the text within the outermost braces

    #remove stuff till first brace from contents
    i = 0
    while i < len(contents):
        letter = contents[i]
        if letter=="{":
            contents=contents[i+1:len(contents)]
            break
        i = i + 1
    #print("after removing 1st brace \n"+contents)
    i = len(contents)-1
    while i >= 0 :
        letter = contents[i]
        if letter=="}":
            contents=contents[0:i]
            break
        i = i - 1
    '''
    wrt = open('writefile.txt', 'w')
    wrt.write(contents)
    wrt.close()
    '''

    return(contents)

def ppWrite(contents,filename):
    #write to file with prettiness
    wrt = open(''+filename+'.txt', 'w')
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
