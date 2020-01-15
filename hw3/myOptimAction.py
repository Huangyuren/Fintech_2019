import numpy as np
import math

def pickMax(value_list):
    maxx = 0
    maxx_id = 0
    for i in range(len(value_list)):
        if value_list[i] > maxx:
            maxx = value_list[i]
            maxx_id = i
    return (maxx, maxx_id)
def myOptimAction(priceMat, transFeeRate):
    # Explanation of my approach:
    # DP Approach
    # Each round we will run through 4 stocks columns and one cash column.
    # At stock's perspective, it will come from retaining previous stock or switching from previous stock or bought by cash.
    # At cash's perspective, it will come from selling another stocks or from previous cash.
    # dp_trace_id will record each stocks/cash origin.
    cash_init = 1000
    hold = 0
    dataLen, stockCount = priceMat.shape
    dp_mat = np.zeros((dataLen, stockCount))    # dp matrix, storing profits at each period for all stocks
    dp_cash_list = []
    actionMat = []
    dp_trace_id = np.zeros((dataLen, stockCount+1))
    day_decision = []
    day_decision_rev = []
    for day in range(dataLen):
        if day == 0:
            for i in range(stockCount):
                dp_mat[day][i] = cash_init*(1-transFeeRate) / priceMat[day][i]
                dp_trace_id[day][i] = -1
            dp_cash_list.append(cash_init)
            dp_trace_id[day][stockCount] = -1
        else:
            iter_candidate = []
            max_value = 0
            for i in range(stockCount+1):         # run through each stock's dp matrix row, i=orig_stock
                dpCandidate = []
                for j in range(stockCount):
                    if j != i and i != stockCount:  #stock turn, switch stock
                        dpCandidate.append(dp_mat[day-1][j]*priceMat[day][j]*pow(1-transFeeRate, 2))
                    elif j != i:     # cash turn, sell stock
                        dpCandidate.append(dp_mat[day-1][j]*priceMat[day][j]*(1-transFeeRate))
                    else:       #stock turn, retain stock
                        dpCandidate.append(dp_mat[day-1][j]*priceMat[day][j])
                if i == stockCount:     #cash turn, retain cash
                    dpCandidate.append(dp_cash_list[-1])
                else:       #stock turn, buy stock
                    dpCandidate.append(dp_cash_list[-1]*(1-transFeeRate))
                (max_value, max_id) = pickMax(dpCandidate)
                if i == stockCount:
                    if max_id == stockCount:
                        dp_cash_list.append(max_value)
                        dp_trace_id[day][stockCount] = max_id
                    else:
                        dp_cash_list.append(max_value)
                        dp_trace_id[day][stockCount] = max_id
                elif max_id == stockCount:
                    dp_mat[day][i] = max_value/priceMat[day][i]
                    dp_trace_id[day][i] = max_id
                else:
                    if max_id == i:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        dp_trace_id[day][i] = max_id
                    else:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        dp_trace_id[day][i] = max_id
    ######BackTracking######
    prev = 0
    for i in reversed(range(1, dataLen)):
        if i == dataLen-1:
            day_decision.append(stockCount)
            prev = int(dp_trace_id[i][stockCount])
        else:
            day_decision.append(prev)
            prev = int(dp_trace_id[i][prev])
    day_decision_rev.append(stockCount)
    for i in range(len(day_decision)):
        day_decision_rev.append(day_decision.pop())
    ######Deciding action matrix######
    for i in range(1, len(day_decision_rev)):
        action = []
        if day_decision_rev[i] == day_decision_rev[i-1]:
            pass
        elif day_decision_rev[i] == stockCount:
            action = [i, day_decision_rev[i-1], -1, dp_mat[i][day_decision_rev[i-1]]*priceMat[i][day_decision_rev[i-1]]]
            actionMat.append(action)
        else:
            if day_decision_rev[i-1] == stockCount:
                action = [i, -1, day_decision_rev[i], dp_cash_list[i-1]]
            else:
                action = [i, day_decision_rev[i-1], -1, dp_mat[i][day_decision_rev[i-1]]*priceMat[i][day_decision_rev[i-1]]]
                actionMat.append(action)
                action = [i, -1, day_decision_rev[i], dp_cash_list[i]]
            actionMat.append(action)
    return actionMat