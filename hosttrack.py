"""
hosttrack - master list of hosts
"""
import csv
import datetime
import glob
import sys
import os.path
import subprocess
import re
master_file = "test_file.txt"
rundate = "not_init"
hosts_dict = {}
justavar = 'X'
just2 = 1

"""
Adding this to try to add to Github
"""
#idx_invm_in = 0
#idx_invm_dt = 1
#idx_dhq_in = 2
#idx_dhq_dt = 3
#idx_mecm_in = 4
#idx_mecm_dt = 5
#idx_ad_in = 6
#idx_ad_dt = 7

def get_name_n_type():

    prompt_text = "Type the name of the input file: \n"
    file_name = input(prompt_text).rstrip()
    if not (os.path.isfile(file_name) and os.access(file_name, os.R_OK)):
        print("File " + file_name + " doesn't exists or is not readable.")
        return "x", "x"
    prompt_text = "Is this an InsightVM list, Desktop HQ list, MECM list, or AD list?\n"
    prompt_text += "Enter I, D, M, or A.\n"
    type_ind = input(prompt_text).rstrip()
    # print("type_ind " + type_ind)
    if len(type_ind) > 1:
        print("Input " + type_ind + " is too long.")
        return "x", "x"
    if not (type_ind.lower() in ["i","d","m","a"]):
        print("Input " + type_ind + " is not a valid choice.")
        return "x", "x"

    return file_name, type_ind.lower()

def clean_input_file(list_in, file_date):
    # find IPs! -> match_ip = re.match(r'(?:\d{1,3}\.){3}\d{1,3}', addr_string) <-
    # find quotes (seen beginning AND end of hostnames
    # find colons - if found, log & ignore the record
    # hostnames only 0-9, a-z plus "-"
    clean_list = []

    for entry in list_in:
        # IP check here
        match_ip = re.match(r'(?:\d{1,3}\.){3}\d{1,3}', entry)
        if match_ip:
            # print/log IP and skip
            # print("Found IP only entry " + entry + ". Skipping it.")
            log_rtn(file_date, "Found IP only entry " + entry + ". Skipping it.")
            continue
        # quote & colon check here
        gut_chk = entry.find(':')
        if gut_chk != -1:
            # print("Odd entry with ':'" + entry + ". Skipping.")
            log_rtn(file_date, "Odd entry with ':'" + entry + ". Skipping.")
            continue
        quote_chk = entry.find('"')
        if quote_chk != -1:
            # print("Odd entry with quotes:" + entry + ". Skipping.")
            log_rtn(file_date,"Odd entry with quotes:" + entry + ". Skipping.")
            continue
        dot = entry.find('.')
        if dot == -1:
            pass
        else:
            entry = entry[0:dot]
        clean_list.append(entry.lower())

    return clean_list

def process_input_file(hosts_dict, file_date):
    rundate = datetime.datetime.now().strftime("%m/%d/%y")
    dirty_input_list = []
    input_list = []
    temp_master = []
    file_name, type_ind = get_name_n_type()
    if (file_name == 'x'):
        sys.exit(2)


    with open(file_name, 'r') as infile:
        for line in sorted(infile):
            dirty_input_list.append(line)
    # if file is empty, error, return False

    input_list = clean_input_file(dirty_input_list, file_date)

    temp_master, idx = make_temp_master(type_ind,hosts_dict)
    if (len(temp_master) == 0):
        # print("No known hosts in master with type " + type_ind)
        log_rtn(file_date,"No known hosts in master with type " + type_ind + ".")
    else:
        for found_in_master in temp_master:
            if found_in_master in input_list:
                # update master for that host for today's date
                # print("Host " + found_in_master + " will be updated. dict is " + str(type(hosts_dict)))
                # print("Host " + found_in_master + " will be updated.")
                log_rtn(file_date, "Host " + found_in_master + " will be updated.")
                #upd_dict(found_in_master, idx, "yes")
                chg_dict("c",found_in_master,type_ind,rundate,hosts_dict)
                # print("dict is " + str(type(hosts_dict)) + " after c")
            else:
                # update master for that host to no for that type for today's date
                # print(found_in_master + " is no longer type " + type_ind + ", dict is " + str(type(hosts_dict)))
                # print(found_in_master + " is no longer type " + type_ind)
                log_rtn(file_date,found_in_master + " is no longer type " + type_ind + ".")
                #upd_dict(found_in_master, idx, "no")
                chg_dict("d",found_in_master,type_ind,rundate,hosts_dict)
                # print("dict is " + str(type(hosts_dict)) + " after d")

        for i in input_list:
            j = i.rstrip("\n")
            if not (j in temp_master):
                # print(j + " to be added to master as " + type_ind + ", dict is " + str(type(hosts_dict)))
                # print(j + " to be added to master as " + type_ind)
                log_rtn(file_date, j + " to be added to master as " + type_ind + ".")
                # add i to master as type with today's date
                chg_dict("a",j,type_ind,rundate,hosts_dict)
                # print("dict is " + str(type(hosts_dict)) + " after a")
            else:
                pass
                # already in master
    # print("proc_input_file hosts_dict has " + str(len(hosts_dict)) + " entries")
    return True

def get_idx4ind(ind_in):

    table = {'i': 0, 'd': 2, 'm': 4, 'a': 6}

    return table[ind_in]

def make_temp_master(ind,hosts_dict):
    temp_list = []
    idx = get_idx4ind(ind)
    for key, value in hosts_dict.items():
        #print("key type is " + str(type(key)))
        if value[idx] == "yes":
            temp_list.append(key)

    return temp_list, idx

def list_masters():
    file_list = []
    input_files = []
    for file in glob.glob("master*.csv"):
        input_files.append(file)
        # print("Found master " + file)
    if (len(input_files) == 0):
        pass
        # print("No master files found.")
    else:
        input_files.sort()
        input_files.reverse()
        file_list = input_files[0]

    return file_list

def cre_dict(list_in,hosts_dict):

    result = True

    if list_in[0] in hosts_dict:
        # print("Duplicate entry " + list_in[0] + " in master file.")
        log_rtn(file_date, "Duplicate entry " + list_in[0] + " in master file.")
        result = False
    else:
        xhost = list_in[0]
        xhost = xhost.lower()
        hosts_dict[xhost] = [list_in[1], list_in[2], list_in[3], list_in[4], list_in[5], list_in[6], list_in[7], list_in[8]]

    return result

def chg_dict(action, host, type_in, date_chgd,hosts_dict):
    result = False
    base_date = "9/10/18"
    idx = get_idx4ind(type_in)
    cktype = type(idx)
    cktype_dict = type(hosts_dict)
    # print("chg_dict idx is " + str(cktype) + ", host is >" + host + "<" + " dict is " + str(cktype_dict) + ".")
    if (action == "a"):
        # do add here w/rundate for type and 9/10/18 for other dates
        # print("a")
        initial_vals = ["no", base_date, "no", base_date, "no", base_date, "no", base_date ]
        initial_vals[idx] = "yes"
        initial_vals[idx+1] = date_chgd
        hosts_dict[host] = initial_vals
        result = True

    elif (action == "c"):
        # do change for type w/rundate, leave others alone
        # print("c")
        hosts_dict[host][idx] = 'yes'
        hosts_dict[host][idx+1] = date_chgd
        result = True

    elif (action == "d"):
        # do 'del' - upd type to 'no' w/rundate
        # print("d")
        # print("In d: " + str(hosts_dict[host]))
        hosts_dict[host][idx] = 'no'
        hosts_dict[host][idx+1] = date_chgd
        # print("Aft d: " + str(hosts_dict[host]))
        result = True

    else:
        print("Something went horribly wrong in chg_dict.")
        sys.exit(2)

    return result

def readmaster(hosts_dict, file_date):
    rec_count = 0
    master_file = list_masters()
    # print("List of masters " + master_file)
    if (len(master_file) > 0):
        print("Using " + master_file + " for input.")
        log_rtn(file_date, "Using " + master_file + " for input.")
    else:
        return rec_count

    with open(master_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # if row[0:1] == "#":
            if row[0][0:1] == "#":
                # if rec_count == 0:
                print("row is " + str(type(row)))
                pass
            else:
                # print("got past first row")
                isok = cre_dict(row,hosts_dict)
            rec_count += 1

    print("readmaster hosts_dict has " + str(len(hosts_dict)) + " entries")
    return rec_count

def writemaster(hosts_dict, file_date):
    result = True
    # prompt_text = "Input name for new Master File: \n"
    # file_name = input(prompt_text).rstrip()
    # file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = "master" + file_date + ".csv"
    file_tmp = "master" + file_date + ".tmp"
    print("Writing new master " + file_name)
    with open(file_tmp,mode='w') as newmaster:
        master_writer = csv.writer(newmaster, delimiter=',')
        header = ["#hostname#", "in_ivnm", "date_ivnm", "in_dhq", "date_dhq", "in_mecm", "date_mecm", "in_ad","date_ad"]
        master_writer.writerow(header)
        for key in hosts_dict:
            curr_row = [key]
            for i in range(0,8):
                curr_row.append(hosts_dict[key][i])
            master_writer.writerow(curr_row)
    # print("writemaster hosts_dict has " + str(len(hosts_dict)) + " entries")
    cmd_list = ["sort", "--output=" + file_name, file_tmp]
    isok = subprocess.run(cmd_list, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    if not(isok):
        print("sort of master file " + file_name + " failed.")
        result = False
    else:
        if not (os.path.isfile(file_name) and os.access(file_name, os.R_OK)):
            print("Master File " + file_name + " doesn't exists or is not readable.")
            result = False
        else:
            cmd_list = ["rm", file_tmp]
            isok = subprocess.run(cmd_list, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    return result

def log_rtn(logfile_date,message):
    # Module to handle logging program actions
    logfile = "master" + logfile_date + ".log"
    whenlog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = open(logfile, 'a')
    log.write(whenlog + " " + message + "\n")
    log.close()

if __name__ == "__main__":
    # 1. eliminate returning hosts_dict when sending in func call
    # 2. try moving declaration up to top of file (where it was before

    # print("Start")
    rundate = datetime.datetime.now().strftime("%m/%d/%y")
    print("Start Date " + rundate + "\n")
    file_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #print("File date: " + file_date)
    # print("B4 readmaster hosts_dict has " + str(len(hosts_dict)) + " entries")

    recs = readmaster(hosts_dict, file_date)
    if recs == 0:
        print("No master files.")
        sys.exit(2)
    else:
        print("readmaster: " + str(recs) + " were processed.")
    # print("Aft readmaster hosts_dict has " + str(len(hosts_dict)) + " entries")

    # temp_master = make_temp_master()
    # if (len(temp_master) == 0):
        # print("Unable to make temp_master.")
        # sys.exit(2)

    isok = process_input_file(hosts_dict, file_date)
    if not isok:
        print("Unable to process input file.")
        sys.exit(2)
    print("Aft process_input_file hosts_dict has " + str(len(hosts_dict)) + " entries")

    # recs = upd_recs_test()
    # print("test: " + str(recs) + " updated.\n")

    isok = writemaster(hosts_dict, file_date)
    print("Aft writemaster hosts_dict has " + str(len(hosts_dict)) + " entries")
    print("Done.\n")
