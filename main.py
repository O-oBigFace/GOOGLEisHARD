import os
import pandas
import time
from Spider import Spider,logger
import json
import sys
from multiprocessing import Process
path_tag_csv = os.path.join(os.getcwd(), "CSVs", "remedy_0809.csv")
path_dir_result = os.path.join(os.getcwd(), "result_file")

mat = pandas.read_csv(path_tag_csv)
mat = mat.fillna(value="")
affiliation_list = mat.iloc[:, 1].values.tolist()
MAXSIZE = 5660


def save_file(filename, list):
    with open(filename, "a", encoding="utf-8") as f:
        for l in list:
            f.write(json.dumps(l) + "\n")


def spider(begin, end):
    print("%d | %d" % (begin, end))
    path = os.path.join(path_dir_result, "%d_%d") % (begin, int(time.time()) % 1000)

    with open(path, "w", encoding="utf-8") as f:
        pass
    sp = Spider()
    result_list = []
    for i in range(begin, end):
        sp.monitor = i
        country = sp.get_country(affiliation_list[i])
        address = sp.get_address(affiliation_list[i])
        item = (i, country, address)
        result_list.append(item)
        if i % 10 == 0 or i == end - 1:
            save_file(path, result_list)
            logger.info("%d | %s | %s" % item)


if __name__ == '__main__':
    # print(affiliation_list)
    # begin = int(sys.argv[1])
    # end = int(sys.argv[2])
    # num_of_process = int(sys.argv[3])
    begin = 1
    end = 10
    num_of_process = 3

    quarter = round((end - begin) / num_of_process)

    args = [(begin + i * quarter, begin + (1+i) * quarter) for i in range(num_of_process-1)]
    args.append((begin + (num_of_process - 1) * quarter, end))

    for a in args:
        p = Process(target=spider, args=a)
        p.start()
        # time.sleep(5)
