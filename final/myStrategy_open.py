import sys
import threading
import numpy as np
import pandas as pd
import bestParamViaExhaustiveSearch

def computeReturnRate(dailyOhlcv, windowSize_1, windowSize_2, ceiling, floor):
    openVec = dailyOhlcv["open"].values
    capital=500000    # Initial available capital
    capitalOrig=capital  # original capital
    transFee = 100
    dataCount=len(openVec)             # day size
    suggestedAction=np.zeros((dataCount,1)) # Vec of suggested actions
    stockHolding=np.zeros((dataCount,1))    # Vec of stock holdings
    total=np.zeros((dataCount,1))       # Vec of total asset
    realAction=np.zeros((dataCount,1))  # Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
    # Run through each day
    for ic in range(dataCount):
        currentPrice=openVec[ic]   # current price
        # suggestedAction[ic]=myStrategy(openVec[0:ic], currentPrice, windowSize_1, alpha, beta)       # Obtain the suggested action
        suggestedAction[ic]=bestParamViaExhaustiveSearch.myStrategy_RSI(openVec[0:ic], currentPrice, windowSize_1, windowSize_2, ceiling, floor)       # Obtain the suggested action
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
    openPricev = dailyOhlcv["open"].tail(evalDays).values
    clearPrice = dailyOhlcv.iloc[-3]["close"]
    beg_index = 0
    windowSizeMin=5; windowSizeMax=20;
    ceilingMin=50; ceilingMax=100
    floorMin=0; floorMax=50
    windowSizeRange = np.arange(5, 25, 5)
    windowSizeBest_1 = windowSizeBest_2 = floorBest = ceilingBest = returnRateBest = 0
    # Start exhaustive search
    for j in range(windowSizeRange[end_index]-4, windowSizeRange[end_index]+1):
        for windowSize_1, windowSize_2 in zip(range(windowSizeMin, windowSizeMax+1), range(windowSizeMin+j, windowSizeMax+j)):
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

