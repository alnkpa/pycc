import os

for dir in os.walk('test'):
    for file in dir[2]:
        spl = file.split('.')
        try:
            if spl[1] == 'py':
                fObj = open(dir[0] + os.sep + file,'w')
                inFile = fObj.read()
                inFile.replace('    ','\t')
                fObj.write(inFile)        
        except:
            pass

