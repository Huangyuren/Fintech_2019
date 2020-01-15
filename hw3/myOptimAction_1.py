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
    dp_mat = np.zeros((stockCount, dataLen))    # dp matrix, storing profits at each period for all stocks
    dp_direction = np.zeros((stockCount+1, dataLen))
    dp_cash_list = []
    actionMat = []
    day_job = []
    for day in range(0, dataLen):
        #######construct dp matrix#######
        if day == 0:
            for i in range(stockCount):
                dp_mat[i][day] = cash_init*(1-transFeeRate) / priceMat[day][i]
            dp_cash_list.append(cash_init)
            day_job.append(stockCount)
        else:
            iter_candidate = []
            equi_cash = 0
            for i in range(stockCount):         # run through each stock's dp matrix row, i=orig_stock
                dpCandidate = []
                for j in range(stockCount):
                    if j == i:                  #keep stocks
                        dpCandidate.append(dp_mat[i][day-1]*priceMat[day][j])
                    else:                       #another stocks to i stock
                        dpCandidate.append(dp_mat[j][day-1]*priceMat[day][j])
                #         iCanBuy = (dp_mat[j][day-1]*priceMat[day][j]*pow(1-transFeeRate, 2)) / priceMat[day][i]     #number of stock i to buy
                #         dpCandidate.append(iCanBuy)
                # (maxi, maxi_id) = pickMax(dpCandidate)
                # equi_cash = maxi*priceMat[day][i]
                (equi_cash, maxi_id) = pickMax(dpCandidate)
                if equi_cash > dp_cash_list[day-1]:
                    dp_mat[i][day] = equi_cash*pow(1-transFeeRate, 2) / priceMat[day][i]
                else:
                    dp_mat[i][day] = (dp_cash_list[day-1]*(1-transFeeRate))/priceMat[day][i]
                    equi_cash = dp_cash_list[day-1]*(1-transFeeRate)
                iter_candidate.append(equi_cash)
            (day_action_gain, day_action_id) = pickMax(iter_candidate)
            if day_action_gain > dp_cash_list[day-1]:
                dp_cash_list.append(day_action_gain)
                day_job.append(day_action_id)
            else:
                dp_cash_list.append(dp_cash_list[day-1])
                day_job.append(stockCount)
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
    print(actionMat[-1][3])
    return actionMat