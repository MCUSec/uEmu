import numpy as np
import sys

readBBR = [] #BB Range file
readTBA = [] #TB Address file
RBB = []

if __name__ == '__main__':
    File_TBA = sys.argv[1]
    File_BBR = sys.argv[2]
    readBBR = np.loadtxt(File_BBR, dtype=str)
    readTBA = np.loadtxt(File_TBA, dtype=str)
    bbr = [[0] * 2 for _ in range(len(readBBR)+1)]
    tba = [0 for _ in range(len(readTBA))]
    for i in range(len(readBBR)):
        bbr[i][0] = int(readBBR[i][0], 16)
        bbr[i][1] = int(readBBR[i][1], 16)
    for i in range(len(readTBA)):
        tba[i] = int(readTBA[i], 16)
    tba.sort()

    bbr[len(readBBR)][0] = -1
    bbr[len(readBBR)][1] = -1

    m=0
    for i in range(len(bbr)-1):
        k = 0
        temp=""
        for j in range(m,len(tba)):
            if tba[j] >= bbr[i][0] and tba[j] < bbr[i][1]:
                k=1
                temp = temp + str(hex(tba[j])) + " "
                m = m + 1
            elif bbr[i+1][0]!=tba[j] and bbr[i][1]==tba[j]:
                k=1
                temp = temp + str(hex(tba[j])) + " "
                m = m + 1
            else:
                break
        if k==1:
            temp = str(hex(bbr[i][0])) + "-" + str(hex(bbr[i][1])) + ":" + temp
            RBB.append(temp)

    RBB.append(str(len(RBB)))
    s = '\n'
    file=open('bb_coverage.txt','w')
    file.write(s.join(RBB))
    file.close()

    print("Reached BB number = " + str(len(RBB)-1))
    print("BB coverage = "str(round((len(RBB)-1)/len(readBBR),2)))



