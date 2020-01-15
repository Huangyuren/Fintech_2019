import csv
import numpy as np
import calendar
import sys

with open(sys.argv[1], newline='', encoding='big5') as csvfile:
    next(csvfile)

    curr_date = 0
    curr_month = 0
    curr_year = 0
    curr_prod_code = "TX"
    due_month = 0
    open_ = 0
    high = 0
    low = 30000
    close = 0
    close_time = 0

    spamreader = csv.reader(csvfile)
    for row in spamreader:
        content = list(row[i] for i in range(5))
        curr_year = int(content[0][0]+content[0][1]+content[0][2]+content[0][3])
        curr_month = int(content[0][4]+content[0][5])
        curr_date = int(content[0][6]+content[0][7])
        break
    month_tuple = calendar.monthrange(curr_year, curr_month)
    # print("month_tuple: ", month_tuple[0], month_tuple[1])
    if calendar.weekday(curr_year, curr_month, curr_date) == 4:
        curr_date = curr_date+3             # check special case: friday
        if curr_date > month_tuple[1]:      # in case exceed month
            curr_date = curr_date - month_tuple[1]
            curr_month = curr_month+1
            due_month = curr_month
        elif month_tuple[0] > 2:              # check whether within third wednesday or not
            third_wednes = 10-month_tuple[0]+14
            if curr_date > third_wednes:
                due_month = curr_month+1
            else:
                due_month = curr_month
        else:
            third_wednes = 3-month_tuple[0]+14
            if curr_date > third_wednes:
                due_month = curr_month+1
            else:
                due_month = curr_month
    else:
        curr_date = curr_date+1
        if curr_date > month_tuple[1]:
            curr_date = curr_date-month_tuple[1]
            curr_month = curr_month+1
            due_month = curr_month
        if month_tuple[0] > 2:              # check whether within third wednesday or not
            third_wednes = 10-month_tuple[0]+14
            if curr_date > third_wednes:
                due_month = curr_month+1
            else:
                due_month = curr_month
        else:
            third_wednes = 3-month_tuple[0]+14
            if curr_date > third_wednes:
                due_month = curr_month+1
            else:
                due_month = curr_month

    first_time = True
    for row in spamreader:
        content = list(row[i] for i in range(5))
        date = int(content[0][6]+content[0][7])
        month = int(content[2][4]+content[2][5])
        deal_timming = int(content[3])
        deal_price = float(content[4])
        if date == curr_date:
            product_code = content[1][0]+content[1][1]
            if product_code == curr_prod_code:
                if month == due_month:
                    if deal_timming >= 84500 and deal_timming <= 134500:
                        if deal_price > 0:
                            close = deal_price
                            close = int(close)
                            if first_time:
                                open_ = deal_price
                                open_ = int(open_)
                                first_time = False
                            if deal_price > high:
                                high = deal_price
                                high = int(high)
                            if deal_price < low:
                                low = deal_price
                                low = int(low)
    # print("=========================INFO=========================")
    # print("Required due month: ", due_month)
    # print("current date: {}0{}{}, current product code: {}".format(curr_year, curr_month, curr_date, curr_prod_code))
    # print("Overall qualified deals: ", deal_counter)
    # print("Open, high, low, close: ", open_, high, low, close)
    print(open_, high, low, close)
