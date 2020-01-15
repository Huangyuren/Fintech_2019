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
    # 1. Technical indicator used: Watch next day price
    # 2. if next day price > today price + transFee ==> buy
    #       * buy the best stock
    #    if next day price < today price + transFee ==> sell
    #       * sell if you are holding stock
    # 3. You should sell before buy to get cash each day
    # default
    cash_init = 1000
    hold = 0
    # user definition
    dataLen, stockCount = priceMat.shape
    dp_mat = np.zeros((dataLen, stockCount))    # dp matrix, storing profits at each period for all stocks
    # dp_direction = np.zeros((stockCount+1, dataLen))
    dp_cash_list = []
    actionMat = []
    dp_trace_id = np.zeros((dataLen, stockCount+1))
    day_decision = []
    day_decision_rev = []
    for day in range(dataLen):
        # print("At day: {}, {}".format(day, priceMat[day]))
        if day == 0:
            for i in range(stockCount):
                dp_mat[day][i] = cash_init*(1-transFeeRate) / priceMat[day][i]
                dp_trace_id[day][i] = -1
                # print("DP_Mat[{}][{}]: {}".format(day, i, dp_mat[day][i]))
            dp_cash_list.append(1000.0)
            dp_trace_id[day][stockCount] = -1
            # print("Day: {}, DP_Cash_list: {}".format(day, dp_cash_list[-1]))
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
                # print("Day: {}, stock: {}, dpCandidate = {}".format(day, i, dpCandidate))
                (max_value, max_id) = pickMax(dpCandidate)
                if i == stockCount:
                    if max_id == stockCount:
                        dp_cash_list.append(max_value)
                        dp_trace_id[day][stockCount] = max_id
                        # print("CashList {}, retain cash: {}".format(i, max_value))
                    else:
                        dp_cash_list.append(max_value)
                        dp_trace_id[day][stockCount] = max_id
                        # print("CashList {}, sell stock {} to get cash: {}".format(i, max_id, dp_cash_list[-1]))
                elif max_id == stockCount:
                    dp_mat[day][i] = max_value/priceMat[day][i]
                    dp_trace_id[day][i] = max_id
                    # print("Stock {}, using Cash: {}, to buy #: {} stocks".format(i, max_value, dp_mat[day][i]))
                else:
                    if max_id == i:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        dp_trace_id[day][i] = max_id
                        # print("Stock {}, retain from stock {} to get {} stocks".format(i, max_id, dp_mat[day][i]))
                    else:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        dp_trace_id[day][i] = max_id
                        # print("Stock {}, to exchange from stock {} to get {} stocks".format(i, max_id, dp_mat[day][i]))
    prev = 0
    for i in reversed(range(1, dataLen)):
        if i == dataLen-1:
            day_decision.append(stockCount)
            prev = int(dp_trace_id[i][stockCount])
            # print("i: {}, prev = {}".format(i, prev))
        else:
            day_decision.append(prev)
            prev = int(dp_trace_id[i][prev])
            # print("i: {}, prev = {}".format(i, prev))
    day_decision_rev.append(stockCount)
    for i in range(len(day_decision)):
        day_decision_rev.append(day_decision.pop())
    # print(day_decision_rev)
    ######decide action matrix######
    for i in range(1, len(day_decision_rev)):
        # print("day job %d: %d" % (i, day_decision_rev[i]))
        action = []
        if day_decision_rev[i] == day_decision_rev[i-1]:
            # print("{} Day job, action: {}, same as yesterday, equivalent cash: {}".format(i, day_decision_rev[i], dp_cash_list[i]))
            pass
        elif day_decision_rev[i] == stockCount:
            # print("{} Day job, action: {}, sell stocks held, equivalent cash: {}".format(i, day_decision_rev[i], dp_cash_list[i]))
            action = [i, day_decision_rev[i-1], -1, dp_mat[i][day_decision_rev[i-1]]*priceMat[i][day_decision_rev[i-1]]]
            actionMat.append(action)
        else:
            if day_decision_rev[i-1] == stockCount:
                # print("{} Day job, action: {}, buy stocks using cash: {}".format(i, day_decision_rev[i], dp_cash_list[i-1]))
                action = [i, -1, day_decision_rev[i], dp_cash_list[i-1]]
            else:
                # print("{} Day job, action: {}, switch stocks, equivalent cash: {}".format(i, day_decision_rev[i], dp_cash_list[i]))
                # action = [i, day_decision_rev[i-1], day_decision_rev[i], dp_cash_list[i-1]]
                action = [i, day_decision_rev[i-1], -1, dp_mat[i][day_decision_rev[i-1]]*priceMat[i][day_decision_rev[i-1]]]
                actionMat.append(action)
                action = [i, -1, day_decision_rev[i], dp_cash_list[i]]
            actionMat.append(action)
    # print (actionMat)
    # print(dp_cash_list[-1])

    return actionMat