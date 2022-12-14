#
#  procmon_csv_filter.py
#  caladium
#
#  Created by Declan Kelly on 25-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import os, sys

def main(argv):
    if len(argv) <= 2:
        return 1

    csv_file_location = argv[1]
    arg_pid_list = [int(i) for i in argv[2:]]
    pid_list = []

    f = open(csv_file_location, encoding="utf-8-sig")
    csv_file_data = [*map(lambda record: record.strip('"'), f.read().split('"\n"'))]
    f.close()

    csv_file_tmp_location = argv[1] + ".tmp"
    f_tmp = open(csv_file_tmp_location, "w", encoding="utf-8")
    f_tmp.write('"{}"\n'.format(csv_file_data[0]))
    for record_line in csv_file_data[1:]:
        record = record_line.split('","')
        if int(record[2]) in arg_pid_list and record[1] == "Start.exe":
            pid_list += [int(record[2])]

        if int(record[2]) in pid_list:
            f_tmp.write('"{}"\n'.format(record_line))
            if record[3] == "Process Create":
                pid_list += [int(record[6].split()[1][:-1])]
    f_tmp.close()

    os.remove(csv_file_location)
    os.rename(csv_file_tmp_location, csv_file_location)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

