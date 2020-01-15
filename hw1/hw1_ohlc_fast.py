import csv
import numpy as np
# import calendar
import sys

open_ = None
high = 0
low = 20000
close = None
very_first = True
# very_first_date = True
# friday = False
# default_date = None
default_due_month = 300000
# curr_year = curr_month = curr_date = None
with open(sys.argv[1], newline='', encoding='big5') as csvfile:
    next(csvfile)
    spamreader = csv.reader(csvfile)
    curr_prod_code = "TX"
    for row in spamreader:
        product_code = row[1][0]+row[1][1]
        if product_code == curr_prod_code:
            if int(row[3]) >= 84500 and int(row[3]) <= 134500 and '/' not in row[2] and int(row[2]) <= default_due_month:
                default_due_month = int(row[2])
                if float(row[4]) > 0:
                    close = float(row[4])
                    if very_first:
                        open_ = float(row[4])
                        very_first = False
                    if float(row[4]) > high:
                        high = float(row[4])
                    if float(row[4]) < low:
                        low = float(row[4])
    open_ = int(open_)
    high = int(high)
    low = int(low)
    close = int(close)
    print(open_, high, low, close)