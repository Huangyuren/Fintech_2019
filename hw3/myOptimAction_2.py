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
    day_job_rev = []
    day_job = []
    for day in range(dataLen):
        print("At day: {}, {}".format(day, priceMat[day]))
        #######construct dp matrix#######
        if day == 0:
            for i in range(stockCount):
                dp_mat[day][i] = cash_init*(1-transFeeRate) / priceMat[day][i]
                print("DP_Mat[{}][{}]: {}".format(day, i, dp_mat[day][i]))
            dp_cash_list.append(cash_init)
            print("Day: {}, DP_Cash_list: {}".format(day, dp_cash_list[-1]))
        else:
            iter_candidate = []
            max_value = 0
            for i in range(stockCount+1):         # run through each stock's dp matrix row, i=orig_stock
                dpCandidate = []
                for j in range(stockCount):
                    if j != i and i != stockCount:  #stock turn, switch stock
                        dpCandidate.append(dp_mat[day-1][j]*priceMat[day][j]*pow(1-transFeeRate, 2))
                    elif j!= i:     # cash turn, sell stock
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
                        print("CashList {}, retain cash: {}".format(i, max_value))
                    else:
                        dp_cash_list.append(max_value)
                        print("CashList {}, sell stock {} to get cash: {}".format(i, max_id, dp_cash_list[-1]))
                elif max_id == stockCount:
                    dp_mat[day][i] = max_value/priceMat[day][i]
                    print("Stock {}, using Cash: {}, to buy #: {} stocks".format(i, max_value, dp_mat[day][i]))
                else:
                    if max_id == i:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        print("Stock {}, retain from stock {} to get {} stocks".format(i, max_id, dp_mat[day][i]))
                    else:
                        dp_mat[day][i] = max_value/priceMat[day][i]
                        print("Stock {}, to exchange from stock {} to get {} stocks".format(i, max_id, dp_mat[day][i]))
    for i in reversed(range(dataLen)):
        temp_list = []
        for j in range(len(dp_mat[i])):
            temp_val = dp_mat[i][j]*priceMat[i][j]
            temp_list.append(temp_val)
        (row_max_val, row_max_id) = pickMax(temp_list)
        if row_max_val > dp_cash_list[i]:
            day_job_rev.append(row_max_id)
        else:
            day_job_rev.append(stockCount)
    for i in range(len(day_job_rev)):
        day_job.append(day_job_rev.pop())



    # print("day_job 0: ", day_job[0])
    ######decide action matrix######
    for i in range(1, len(day_job)):
        # print("day job %d: %d" % (i, day_job[i]))
        action = []
        if day_job[i] == day_job[i-1]:
            # print("{} Day job, action: {}, same as yesterday, equivalent cash: {}".format(i, day_job[i], dp_cash_list[i]))
            pass
        elif day_job[i] == stockCount:
            # print("{} Day job, action: {}, sell stocks held, equivalent cash: {}".format(i, day_job[i], dp_cash_list[i]))
            action = [i, day_job[i-1], -1, dp_cash_list[i]]
            actionMat.append(action)
        else:
            if day_job[i-1] == stockCount:
                # print("{} Day job, action: {}, buy stocks using cash: {}".format(i, day_job[i], dp_cash_list[i-1]))
                action = [i, -1, day_job[i], dp_cash_list[i-1]]
            else:
                # print("{} Day job, action: {}, switch stocks, equivalent cash: {}".format(i, day_job[i], dp_cash_list[i]))
                action = [i, day_job[i-1], day_job[i], dp_cash_list[i-1]]
            actionMat.append(action)
    print(dp_cash_list[-1])
    return actionMat