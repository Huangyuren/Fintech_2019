import threading
import multiprocessing
import numpy as np
import sys
import time
import myStrategy_close


if __name__ == "__main__":
    # For threading library
    # def job(end_index):
    #     print("Begin index:", end_index)
    #     myStrategy_high.training(end_index)

    # threads = []
    # for i in range(6):
    #     threads.append(threading.Thread(target=job, args=(i,)))
    #     threads[i].start()
    # for i in range(6):
    #     threads[i].join()
    # print("Done.")

    # For multiprocess library
    sta = time.time()
    def job(end_index, q):
        print("End index:", end_index)
        time.sleep(2)
        result_param = myStrategy_close.training(end_index)
        q.put(result_param)

    q = multiprocessing.Queue()
    process = []
    for i in range(1,8):
        process.append(multiprocessing.Process(target=job, args=(i,q,)))
        process[i-1].start()
    for i in range(7):
        process[i].join()
    for i in range(7):   
        print("Core index: {}, result: {}".format(i, q.get()))
    print("Close info.")
    print("Time elapsed: ", time.time()-sta)
