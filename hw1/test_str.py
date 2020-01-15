import csv
import numpy as np
import calendar

with open('csv_file/Daily_2018_08_20.csv', newline='', encoding='big5') as csvfile:
    next(csvfile)
    spamreader = csv.reader(csvfile)
    curr_prod_code = "TX"
    curr_date = 20
    for row in spamreader:
        content = list(row[i] for i in range(5))
        date = int(content[0][6]+content[0][7])
        if date == curr_date:
            product_code = content[1][0]+content[1][1]
            # print(len(product_code), product_code, curr_prod_code)
            if product_code == curr_prod_code:
                print("stage 2: ", product_code)
