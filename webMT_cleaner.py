import csv, math
import glob, os, sys

MT_NON_DATA_ROWS = 24
MT_DATA_BLOCK_NUM = 6
MT_BLOCK_NAMES = ["Obsolete", "Scaled X", "Scaled Y", "Raw X", "Raw Y" , "Time"]
MAX_TIME_GAP = 20
DESIRED_TIME_GAP = 15

def readFile(mtFile):
    if v > 2:
        with open(mtFile,'r',newline='') as fileObj:
            mtReader = csv.reader(fileObj, delimiter = ",",)
            for mtLine in mtReader:
                try:
                    if mtLine[0] != '':
                        mtContents.append(mtLine)
                    else:
                        mtContents.append([])
                except:
                    mtContents.append([])
    else:
        with open(mtFile,'r') as fileObj:
            mtReader = csv.reader(fileObj, delimiter = ",",)
            for mtLine in mtReader:
                try:
                    if mtLine[0] != '':
                        mtContents.append(mtLine)
                    else:
                        mtContents.append([])
                except:
                    mtContents.append([])

    while mtContents[-1] == [''] or mtContents[-1] == []:
        mtContents.pop()
    return

def parseFirstLine(firstLine):
    global subjID
    subjID = str(firstLine[0])
    global trialNum
    trialNum = int(firstLine[1])
    print("\nSubject: " + subjID + " supposedly completed " + str(trialNum) + " trials.")
    return

def findBlockBoundaries():
    global blockBoundaries
    for mtLine in range(mtLength):
        try:
            if mtContents[mtLine][0] == '':
                blankLines.append(mtLine)
        except:
            blankLines.append(mtLine)
    for blankLine in range(len(blankLines)):
        if blankLine % 2 == 0:
            blockBoundaries[int(blankLine/2)].append(blankLines[blankLine]+1)
        else:
            blockBoundaries[int(blankLine/2)].append(blankLines[blankLine]-1)
    blockBoundaries[MT_DATA_BLOCK_NUM - 1].append(mtLength - 1)

def checkBlockLengths(attempt=1):
    global trialNum
    global blockSize
    for blockNum, blockName in zip(range(MT_DATA_BLOCK_NUM),MT_BLOCK_NAMES):
        blockSize = blockBoundaries[blockNum][1] - blockBoundaries[blockNum][0]
        blockLengths.append(blockSize)
    blockMin = min(blockLengths)
    for n in range(len(blockLengths)):
        if blockLengths[n] > blockMin:
            blockBoundaries[n][1]=blockBoundaries[n][0]+blockMin
    global mtContents
    if mtContents[0][1] != blockMin:
        mtContents[0][1] = blockMin-1
        print("\nNumber of trials successfully corrected in header!")
    else:
        print("\nAll blocks have the proper length\n")
    # if all(blockLength == trialNum+1 for blockLength in blockLengths):
        # if attempt==1:
            
            # return
        # else:
            # global mtContents
            # mtContents[0][1] = trialNum
            
            # return
    if all(blockLength != trialNum+1 for blockLength in blockLengths):
        print("\nNo block lengths match the number of trials in the .mt header")
        if attempt==1:
            print("\nAttempting to auto-correct")
            trialNum = blockLengths[0]-1
            checkBlockLengths(2)
        else:
            raise Exception('Failed to auto-correct block lengths. Check number of trials in each block.')
    if blockSize != trialNum + 1:
        print(MT_BLOCK_NAMES[blockNum] + ''' block has the wrong number ('''+ str(blockSize) +''') of trials''')

def checkTimeSeries():
    global obsoleteList, scaledXList, scaledYList, rawXList, rawYList, timeList, mtContents
    obsoleteList = mtContents[blockBoundaries[0][0]+2:blockBoundaries[0][1]+1]
    obsoleteHeader = mtContents[blockBoundaries[0][0]:blockBoundaries[0][0]+2]
    scaledXList = mtContents[blockBoundaries[1][0]+2:blockBoundaries[1][1]+1]
    scaledXHeader = mtContents[blockBoundaries[1][0]:blockBoundaries[1][0]+2]
    scaledYList = mtContents[blockBoundaries[2][0]+2:blockBoundaries[2][1]+1]
    scaledYHeader = mtContents[blockBoundaries[2][0]:blockBoundaries[2][0]+2]
    rawXList = mtContents[blockBoundaries[3][0]+2:blockBoundaries[3][1]+1]
    rawXHeader = mtContents[blockBoundaries[3][0]:blockBoundaries[3][0]+2]
    rawYList = mtContents[blockBoundaries[4][0]+2:blockBoundaries[4][1]+1]
    rawYHeader = mtContents[blockBoundaries[4][0]:blockBoundaries[4][0]+2]
    timeList = mtContents[blockBoundaries[5][0]+2:blockBoundaries[5][1]+1]
    timeHeader = mtContents[blockBoundaries[5][0]:blockBoundaries[5][0]+2]
    for i, time in enumerate(timeList):
        if int(time[17]) == 0:
            timeList[i].pop(17)
            timeList[i].insert(17,1)
        elif int(time[17]) > MAX_TIME_GAP:
            scaledXList[i].insert(17,0)
            scaledYList[i].insert(17,0)
            rawXList[i].insert(17,400)
            rawYList[i].insert(17,600)
            timeList[i].insert(17,1)
            print('x')
        while time[-1] == '' or time[-1]==time[-2]:###Get rid of duplicates at the end
            #print("time[-1] = " + time[-1])
            #print("scaledXList[i][-1]: " + scaledXList[i][-1])
            scaledXList[i].pop(-1)
            scaledYList[i].pop(-1)
            rawXList[i].pop(-1)
            rawYList[i].pop(-1)
            timeList[i].pop(-1)
        j=17
        while True:
        #for j in range(17,len(time)):
            try:
                time[j+1]
            except IndexError:
                break
            timeRange = int(time[j])+5
            nextTime = int(time[j+1])
            itera=0
            while time[j+1] != '' and timeRange >= nextTime and time[j+1]!=time[-1]:
                scaledXList[i].pop(j+1)
                scaledYList[i].pop(j+1)
                rawXList[i].pop(j+1)
                rawYList[i].pop(j+1)
                timeList[i].pop(j+1)
                nextTime = int(timeList[i][j+1])
            try:
                difference = int(time[j+1])-int(time[j])
            except:
                continue
            if difference > MAX_TIME_GAP:
                steps = int(math.floor(difference / DESIRED_TIME_GAP))
                if difference % DESIRED_TIME_GAP == 0:
                    steps -= 1
                if v > 2:
                    temp_range = range(steps)
                else:
                    temp_range = xrange(steps)
                for step in temp_range:
                    scaledXList[i].insert(int(j)+int(step)+1,float(scaledXList[i][j]))
                    scaledYList[i].insert(int(j)+int(step)+1,float(scaledYList[i][j]))
                    rawXList[i].insert(int(j)+int(step)+1,int(round(float(rawXList[i][j]))))
                    rawYList[i].insert(int(j)+int(step)+1,int(round(float(rawYList[i][j]))))
                    timeList[i].insert(int(j)+int(step)+1,int(timeList[i][j])+((int(step)+1)*int(DESIRED_TIME_GAP)))
            j+=1
        if timeList[i][-1] == timeList[i][-2]:
            scaledXList[i].pop(-1)
            scaledYList[i].pop(-1)
            rawXList[i].pop(-1)
            rawYList[i].pop(-1)
            timeList[i].pop(-1)
    for n,scaledX in enumerate(scaledXList):
        for nX,X, in enumerate(scaledX):
            if nX >= 17:
                if float(X) > 1:
                    scaledXList[n][nX] = 1
                elif float(X) < -1:
                    scaledXList[n][nX] = -1
    for n,scaledY in enumerate(scaledYList):
        for nY,Y, in enumerate(scaledY):
            if nY >= 17:
                if float(Y) > 1.5:
                    scaledYList[n][nY] = 1.5
                elif float(Y) < 0:
                    scaledYList[n][nY] = 0
    mtContents=[mtContents[0]]
    mtContents.extend([[]])
    for mtBlockList, mtHeader in zip((obsoleteList, scaledXList, scaledYList, rawXList, rawYList, timeList),(obsoleteHeader, scaledXHeader, scaledYHeader, rawXHeader, rawYHeader, timeHeader)):
        mtContents.extend(mtHeader)
        for mtLine in mtBlockList:
            mtContents.append(mtLine)
        mtContents.extend([[],[]])

def fixScaledXY():
    for n,scaledX in enumerate(scaledXList):
        for nX,X, in enumerate(scaledX):
            if nX >= 17:
                if float(X) > 1:
                    scaledXList[n][nX] = 1
                elif float(X) > -1:
                    scaledXList[n][nX] = -1
    for n,scaledY in enumerate(scaledYList):
        for nY,Y, in enumerate(scaledY):
            if nY >= 17:
                if float(Y) > 1.5:
                    scaledYList[n][nY] = 1.5
                elif float(Y) > 0:
                    scaledYList[n][nY] = 0

def writeCSV(mtFile,attempt=1):
    print("\nWriting new .mt file to " + mtFile)
    try:
        if v > 2:
            with open(mtFile,'w',newline='') as fileObj:
                mtWriter = csv.writer(fileObj, delimiter = ",",)
                for mtLine in mtContents:
                    mtWriter.writerow(mtLine)
        else:
            with open(mtFile,'w') as fileObj:
                mtWriter = csv.writer(fileObj, delimiter = ",",)
                for mtLine in mtContents:
                    mtWriter.writerow(mtLine)
    except IOError:
        if attempt==2:
            exit()
        print('\nMaking "corrected" subfolder...')
        os.makedirs(os.path.dirname(mtFile))
        writeCSV(mtFile,attempt=2)
    print("\nSuccessfully wrote new .mt file to " + mtFile)
    return

def get_input(prompt):
    if v < 3:
        my_input = str(raw_input(prompt))
    else:
        my_input = input(prompt)
    return my_input

def badFile(fileName):
    splitFileName=os.path.split(fileName)
    return os.path.join(splitFileName[0],'bad/',splitFileName[1])

if __name__ == "__main__":
    v = int(sys.version.split()[0].split('.')[0])
    #filePath = get_input('Please enter the path to the files?\n')
    if len(sys.argv) == 2:
        filePath = sys.argv[1]
    else:
		##You can hard code the path in here if you want
        filePath = ''
    if filePath == '':
        print('\nUsage: python webMT_cleaner.py /path/to/folder/with/mt/files')
        exit()
    else:
        #filePath = filePath.replace('\\','/')
        mtList=glob.glob(filePath+"/*.mt")
    print(mtList)
    if not os.path.exists(os.path.join(filePath,'/bad/')):
        os.mkdir(os.path.join(filePath,'/bad/'))
    for mtFile in mtList:
        print(mtFile)
        #if file already exists, go on to next
        if (os.path.isfile(mtFile.replace(os.path.basename(mtFile),"corrected/"+os.path.basename(mtFile)))):
            continue
        mtContents = list()
        subjID = int()
        trialNum = int()
        blockLengths = list()
        blockBoundaries = [[],[],[],[],[],[]]
        blankLines = list()
        obsoleteList = []
        scaledXList = []
        scaledXListOrig = []
        scaledYList = []
        rawXList = []
        rawYList = []
        timeList = []
        mtLength = int()
        print("-------------\nReading " + mtFile)
        readFile(mtFile)
        parseFirstLine(mtContents[0])
        mtLength = len(mtContents)
        findBlockBoundaries()
        checkBlockLengths()
        try:
            checkTimeSeries()
        except:
            badFileName = badFile(mtFile)
            os.rename(mtFile,badFileName)
            continue
        #fixScaledXY()
        writeCSV(mtFile.replace(os.path.basename(mtFile),"corrected/"+os.path.basename(mtFile)))
