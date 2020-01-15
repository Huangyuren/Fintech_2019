import sys
import numpy as np
import pandas as pd
import random

def myStrategy(dailyOhlcvFile,minutelyOhlcvFile, currentOpenPrice):
    #  seedlst = ["random", "ele", "fly", "elect"]
    #  currSeed = seedlst[random.choice([0,1,2,3])]
    #  random.seed(currSeed)
    random_choice = random.choice([-1,0,1])
    #  print("Random choice: {}".format(random_choice))
    #  [7, 22, 89, 3]
    #  [8, 23, 71, 36]
    #  [19, 28, 70, 46]
    windowSize_1 = 8 
    windowSize_2 = 23
    ceiling = 71
    floor = 36
    action=0        # action=1(buy), -1(sell), 0(hold), with 0 as the default action
    dataLen=len(dailyOhlcvFile)       # Length of the data vector
    openVec = dailyOhlcvFile["open"].values
    openVec = np.append(openVec, currentOpenPrice)
    #  print("OpenVec's shape:", openVec.shape)
    if dataLen==0:
        return action
    # Compute rsi
    if dataLen >= windowSize_2:
        windowedData_1=openVec[-windowSize_1:]     # Compute the normal MA using windowSize
        windowedData_2=openVec[-windowSize_2:]
        up = down = 0
        for i in range(1, len(windowedData_1)):
            temp = windowedData_1[i] - windowedData_1[i-1]
            if temp >= 0:
                up += temp
            else:
                down += abs(temp)
        rsi_1 = (up/(up+down))*100
        up = down = 0
        for i in range(1, len(windowedData_2)):
            temp = windowedData_2[i] - windowedData_2[i-1]
            if temp >= 0:
                up += temp
            else:
                down += abs(temp)
        rsi_2 = (up/(up+down))*100
        if rsi_1 >= ceiling:
            action = -1
        elif rsi_1 < floor:
            action = 1
        else:
            if rsi_1 >= rsi_2:
                action = 1
            else:
                action = -1
        #  return action
        if action == random_choice:
            return action
        else:
            return random_choice
    elif dataLen >= windowSize_1:
        windowedData=openVec[-windowSize_1:]     # Compute the normal MA using windowSize
        up = down = 0
        for i in range(1, len(windowedData)):
            temp = windowedData[i] - windowedData[i-1]
            if temp >= 0:
                up += temp
            else:
                down += temp
        rsi = (up/(up+down))*100
        if rsi >= 60:
            action = -1
        else:
            action = 1
        if action == random_choice:
            return action
        else:
            return random_choice
        #  return action
    else:
        return random_choice



