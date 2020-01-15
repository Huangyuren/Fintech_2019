import sys
import numpy as np
import pandas as pd

# Decision of the current day by the current price, with 3 modifiable parameters
def myStrategy_multi_stock(pastPriceVec, currentPrice, stockType):
    # Explanation of my approach:
    # 1. Technical indicator used: MA
    # 2. if price-ma>alpha ==> buy
    #    if price-ma<-beta ==> sell
    # 3. Modifiable parameters: alpha, beta, and window size for MA
    # 4. Use exhaustive search to obtain these parameter values (as shown in bestParamByExhaustiveSearch.py)
    
    # Technical indicator type: TItype [0 1 2 3] matches to [MA RSI] individually
    # stockType='SPY', 'IAU', 'LQD', 'DSI'
    # Set parameters for different stocks
    paramSetting={  'SPY': {'TItype':0, 'alpha':6, 'beta':16, 'windowSize':4},
                    'IAU': {'TItype':1, 'alpha':0, 'beta':2, 'windowSize':26},
                    'LQD': {'TItype':0, 'alpha':0, 'beta':1, 'windowSize':5},
                    'DSI': {'TItype':0, 'alpha':2, 'beta':10, 'windowSize':17}}
    ti_type = paramSetting[stockType]['TItype']
    windowSize=paramSetting[stockType]['windowSize']
    alpha=paramSetting[stockType]['alpha']
    beta=paramSetting[stockType]['beta']
    
    action=0        # action=1(buy), -1(sell), 0(hold), with 0 as the default action
    dataLen=len(pastPriceVec)       # Length of the data vector
    if dataLen==0: 
        return action
    # Compute MA
    if dataLen<windowSize:
        ma=np.mean(pastPriceVec)    # If given price vector is small than windowSize, compute MA by taking the average
    else:
        windowedData=pastPriceVec[-windowSize:]     # Compute the normal MA using windowSize 
        ma=np.mean(windowedData)
    # Determine action
    if (currentPrice-ma)>alpha:     # If price-ma > alpha ==> buy
        action=1
    elif (currentPrice-ma)<-beta:   # If price-ma < -beta ==> sell
        action=-1

    return action
def myStrategy_RSI(pastPriceVec, currentPrice, windowSize_1, windowSize_2, ceiling, floor):
    action=0        # action=1(buy), -1(sell), 0(hold), with 0 as the default action
    dataLen=len(pastPriceVec)       # Length of the data vector
    if dataLen==0:
        return action
    # Compute rsi
    if dataLen >= windowSize_2:
        windowedData_1=pastPriceVec[-windowSize_1:]     # Compute the normal MA using windowSize
        windowedData_2=pastPriceVec[-windowSize_2:]
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
        # print("RSI_1={}, RSI_2={}".format(rsi_1, rsi_2))
        # if rsi_1 >= rsi_2:
        #     action = 1
        # else:
        #     action = -1
        return action
    elif dataLen >= windowSize_1:
        windowedData=pastPriceVec[-windowSize_1:]     # Compute the normal MA using windowSize
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

# Compute return rate over a given price vector, with 3 modifiable parameters
def computeReturnRate(priceVec, windowSize_1, windowSize_2, ceiling, floor):
    capital=1000    # Initial available capital
    capitalOrig=capital  # original capital
    dataCount=len(priceVec)             # day size
    suggestedAction=np.zeros((dataCount,1)) # Vec of suggested actions
    stockHolding=np.zeros((dataCount,1))    # Vec of stock holdings
    total=np.zeros((dataCount,1))       # Vec of total asset
    realAction=np.zeros((dataCount,1))  # Real action, which might be different from suggested action. For instance, when the suggested action is 1 (buy) but you don't have any capital, then the real action is 0 (hold, or do nothing). 
    # Run through each day
    for ic in range(dataCount):
        currentPrice=priceVec[ic]   # current price
        # suggestedAction[ic]=myStrategy(priceVec[0:ic], currentPrice, windowSize_1, alpha, beta)       # Obtain the suggested action
        suggestedAction[ic]=myStrategy_RSI(priceVec[0:ic], currentPrice, windowSize_1, windowSize_2, ceiling, floor)       # Obtain the suggested action
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

if __name__=='__main__':
    returnRateBest=-1.00     # Initial best return rate
    df=pd.read_csv(sys.argv[1]) # read stock file
    adjClose=df["Adj Close"].values     # get adj close as the price vector
    print("All #Adj close: ", len(adjClose))
    windowSizeMin=5; windowSizeMax=30;   # Range of windowSize to explore
    ceilingMin=50; ceilingMax=100
    floorMin=0; floorMax=50
    windowSizeRangeLong = np.arange(5, 35, 5)
    windowSizeRangeShort = np.arange(5, 20, 5)
    # Start exhaustive search
    for winspan_short in windowSizeRangeShort:
        for winspan_long in windowSizeRangeLong:
            for windowSize_1, windowSize_2 in zip(range(windowSizeMin+winspan_short, windowSizeMax+winspan_short+1), range(windowSizeMin+winspan_long, windowSizeMax+winspan_long+1)):
                for ceiling in range(ceilingMin, ceilingMax+1):
                    for floor in range(floorMin, floorMax+1):
                        print("windowSize_1=%d, windowSize_2=%d, floor=%d, ceiling=%d" %(windowSize_1, windowSize_2, floor, ceiling), end="")
                        returnRate=computeReturnRate(adjClose, windowSize_1, windowSize_2, ceiling, floor)     # Start the whole run with the given parameters
                        print(" ==> returnRate=%f " %(returnRate))
                        if returnRate > returnRateBest:     # Keep the best parameters
                            windowSizeBest_1=windowSize_1
                            windowSizeBest_2=windowSize_2
                            floorBest = floor
                            ceilingBest = ceiling
                            returnRateBest=returnRate
    print("Best settings: windowSize_1=%d, windowSize_2=%d, floor=%d, ceiling=%d ==> returnRate=%f" %(windowSizeBest_1, windowSizeBest_2, floorBest, ceilingBest, returnRateBest))