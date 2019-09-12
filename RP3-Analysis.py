# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 21:20:02 2019

@author: Jake
"""


import matplotlib.pyplot as plt
import numpy as np

#RP3 Force data is set to the minimum integer after the end of the drive.
#It makes more sense to think of the drive as having 0 force where undefined, so I set negative numbers to 0.
def minZero(listOfNums):
    for i in range(len(listOfNums)):
        listOfNums[i] = max(0, listOfNums[i])
    return listOfNums
    
##Given a csv filename, read in the relevant data. 
def readData(fileName):
    file = open(fileName, "r")
    
    ### get the length of each RP3 Piece
    f = file.read().split('\n')
    validLines = f[1:len(f)-2]
    
    commaSep = [line.split(',') for line in validLines]
    pieceLengths = []
    pieceLength = 1
    for i in commaSep[1:]:
        if i[3] =='1':
            pieceLengths.append(pieceLength-1)
            pieceLength = 0
        pieceLength +=1
    pieceLengths.append(pieceLength-2)
    ## Get force curves
    curves = [[[0 for k in range(80)] for j in range(i)] for i in pieceLengths]
    maxForces = [[] for i in pieceLengths]
    linesProcessed = 0
    energy= [[0 for j in range(i)] for i in pieceLengths]
    strokeLength= [[0 for j in range(i)] for i in pieceLengths]
    for i in range(len(curves)):
        energy[i] = [float(commaSep[j][12]) for j in range(linesProcessed, linesProcessed + pieceLengths[i])]
        strokeLength[i] = [float(commaSep[j][8]) for j in range(linesProcessed, linesProcessed + pieceLengths[i])]        
        curves[i] = [minZero(list(map(int, validLines[j].split('"')[1].split(',')))) for j in range(linesProcessed, linesProcessed + pieceLengths[i])]
        
        #RP3 measures force at 2.2cm intervals
        maxForces[i] = [int(float(commaSep[j][17])/2.2) for j in range(linesProcessed, linesProcessed + pieceLengths[i])] 
        linesProcessed += pieceLengths[i]+1

    file.close()
    return (curves, maxForces, energy, strokeLength)
    

#Don't include first 2 or last 2 strokes if you want to avoid the front-end-heavy first stroke bias. 
#Especially important for short pieces, but if you're looking at error per stroke over a piece, having a massive error
#on the first stroke(s) makes graphs far less readable, and generally the first and last strokes are massive outliers. 
offset = 2

filename = 'shortBuilder.csv'
fileDir = 'C:\\Users\\Jake\\Downloads\\'
curves, maxForce, energy, strokeLength = readData(fileDir +filename)
averageStrokeLength = [sum(strokeLength[i])/len(strokeLength[i]) for i in range(len(curves))]
curves = [np.array(curves[i]) for i in range(len(curves))]
averageStrokes = [np.zeros(80) for i in curves]

spikes = [[0 for j in i] for i in curves]
for i in range(len(curves)):
    for j in range(offset, len(curves[i])-offset): #ignoring first two and last two strokes. Might error if a piece has fewer than 4 strokes. 
        averageStrokes[i] += curves[i][j]
        for k in range(2, len(curves[i][j])):
            if curves[i][j][k] < curves[i][j][k-1] and curves[i][j][k-1] > curves[i][j][k-2]:
                spikes[i][j] += 1
    if j <= 3:
        print('curves['+str(i)+'] has length ' + str(len(curves[i])) + ' which is probably 6 or less')
    averageStrokes[i] *= 1./float(j-1)
    
averageSpikes = [float(sum(spikeSet))/float(len(spikeSet)) for spikeSet in spikes]

modelCurve = averageStrokes[0]

averageDiffs = [i - modelCurve for i in averageStrokes] 

specificDiffs = [[modelCurve-i  for i in curves[j][offset:len(curves[j])-offset]] for j in range(len(curves))]
averageNormalizedStrokes = [iAverage/sum(iAverage)for iAverage in averageStrokes]
averageNormalizedSpecificDiffs = [normAverage - modelCurve/sum(modelCurve) for normAverage in averageNormalizedStrokes]

plt.figure(figsize = (9, 6))
for i in range(4):
    plt.plot(averageNormalizedSpecificDiffs[i])
