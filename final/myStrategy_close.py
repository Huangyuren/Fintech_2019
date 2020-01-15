import sys
import numpy as np
import pandas as pd
import bestParamViaExhaustiveSearch
import random

def myStrategy_random(dailyOhlcvFile,minutelyOhlcvFile,openPricev):
    random.seed("fly")
    return random.choice([-1,0,1])

def myStrategy(dailyOhlcvFile,minutelyOhlcvFile, currentPrice):
    windowSize_1 = 8
    windowSize_2 = 23
    ceiling = 71
    floor = 36
    action=0        # action=1(buy), -1(sell), 0(hold), with 0 as the default action
    dataLen=len(dailyOhlcvFile)       # Length of the data vector
    closeVec = dailyOhlcvFile["close"].values
    if dataLen==0:
        return action
    # Compute rsi
    if dataLen >= windowSize_2:
        windowedData_1=closeVec[-windowSize_1:]     # Compute the normal MA using windowSize
        windowedData_2=closeVec[-windowSize_2:]
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
        return action
    elif dataLen >= windowSize_1:
        windowedData=closeVec[-windowSize_1:]     # Compute the normal MA using windowSize
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
        return action
    else:
        return action

def computeReturnRate(dailyOhlcv, windowSize_1, windowSize_2, ceiling, floor):
    closeVec = dailyOhlcv["close"].values
    capital=500000    # Initial available capital
    capitalOrig=capital  # original capital
    transFee = 100
    dataCount=len(closeVec)             # day size
    suggestedAction=np.zeros((dataCount,1)) # Vec of suggested actions
    stockHolding=np.zeros((dataCount,1))    # Vec of stock holdings
    total=np.zeros((dataCount,1))       # Vec of total asset
    realAction=np.zeros((dataCount,1))  # Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
    # Run through each day
    for ic in range(dataCount):
        currentPrice=closeVec[ic]   # current price
        # suggestedAction[ic]=myStrategy(closeVec[0:ic], currentPrice, windowSize_1, alpha, beta)       # Obtain the suggested action
        suggestedAction[ic]=bestParamViaExhaustiveSearch.myStrategy_RSI(closeVec[0:ic], currentPrice, windowSize_1, windowSize_2, ceiling, floor)       # Obtain the suggested action
        # get real action by suggested action
        if ic>0:
            stockHolding[ic]=stockHolding[ic-1] # The stock holding from the previous day
        if suggestedAction[ic]==1:  # Suggested action is "buy"
            if stockHolding[ic]==0:     # "buy" only if you don't have stock holding
                stockHolding[ic]=capital/currentPrice # Buy stock using cash
                capital=0   # Cash
                realAction[ic]=1
        elif suggestedAction[ic]==-1:   # Suggested action is "sell"
            if stockHolding[ic]>0:      # "sell" only if you have stock holding
                capital=stockHolding[ic]*currentPrice # Sell stock to have cash
                stockHolding[ic]=0  # Stocking holding
                realAction[ic]=-1
        elif suggestedAction[ic]==0:    # No action
            realAction[ic]=0
        else:
            assert False
        total[ic]=capital+stockHolding[ic]*currentPrice # Total asset, including stock holding and cash 
    returnRate=(total[-1]-capitalOrig)/capitalOrig      # Return rate of this run
    return returnRate

def training(end_index):
    returnRateBest=-1.00     # Initial best return rate
    dailyOhlcv = pd.read_csv(sys.argv[1])
    # minutelyOhlcv = pd.read_csv(sys.argv[2])
    evalDays = 14
    closePricev = dailyOhlcv["close"].tail(evalDays).values
    clearPrice = dailyOhlcv.iloc[-3]["close"]
    beg_index = 0
    windowSizeMin=0; windowSizeMax=15;    # one week to explore
    ceilingMin=50; ceilingMax=100
    floorMin=0; floorMax=50
    windowSizeRange = np.arange(5, 45, 5)    # two months span
    windowSizeBest_1 = windowSizeBest_2 = floorBest = ceilingBest = returnRateBest = 0
    # Start exhaustive search
    for j in range(windowSizeRange[end_index]-4, windowSizeRange[end_index]+1):
        for windowSize_1, windowSize_2 in zip(range(windowSizeMin+windowSizeRange[beg_index], windowSizeMax+windowSizeRange[beg_index]+1), range(windowSizeMin+j, windowSizeMax+j)):
            for ceiling in range(ceilingMin, ceilingMax+1):
                for floor in range(floorMin, floorMax+1):
                    print("EndIndex=%d, WindowSize_1=%d, WindowSize_2=%d, Floor=%d, Ceiling=%d" %(end_index, windowSize_1, windowSize_2, floor, ceiling), end="")
                    # returnRate=computeReturnRate(dailyOhlcv, minutelyOhlcv, evalDays, closePricev, clearPrice, windowSize_1, windowSize_2, ceiling, floor)     # Start the whole run with the given parameters
                    returnRate=computeReturnRate(dailyOhlcv, windowSize_1, windowSize_2, ceiling, floor)
                    print(" ==> returnRate=%f " %(returnRate))
                    if returnRate > returnRateBest:     # Keep the best parameters
                        windowSizeBest_1=windowSize_1
                        windowSizeBest_2=windowSize_2
                        floorBest = floor
                        ceilingBest = ceiling
                        returnRateBest=returnRate
    print("Best settings: windowSize_1=%d, windowSize_2=%d, floor=%d, ceiling=%d ==> returnRate=%f" %(windowSizeBest_1, windowSizeBest_2, floorBest, ceilingBest, returnRateBest))
    return [windowSizeBest_1, windowSizeBest_2, floorBest, ceilingBest, returnRateBest]

