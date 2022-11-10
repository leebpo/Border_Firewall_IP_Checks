# make sure this sits in same directory as
# a folder called 'csv' with 'names.csv', 'objects.csv', and 'rules.csv',
# a folder called 'new_csv' with 'new_names.csv', 'new_objects.csv', and 'new_rules.csv',
# a 'test.txt' file

import pandas as pd
import numpy as np
import copy
import os

# global variables
unfound_dns = "NXDOMAIN"
no_answer = "No answer"
dns_records = {}
dns_pings = {}

# helper function for getting info from csv
def pd_rows_len(csv_addr):
    dataframe = pd.read_csv(csv_addr)
    rows = dataframe.index
    num_rows = len(rows)
    return (dataframe, rows, num_rows)


# used later to print out dictionaries and arrays in a nice format
def print_dict(dictionary, name):
    print(f'{name}:')
    for key in dictionary.keys():
        print("{}{}".format(key.ljust(27), dictionary[key]))
    print("")
    
def print_arr(arr, name):
    print(f'{name}:')
    for elem in arr:
        print(elem)
    print("")
    
    
# helper functions for identifying host names & IPs
def is_hostname(word):
    dot_endings = [".edu", ".net", ".com", ".org", ".gov"]
    return (word[-4:] in dot_endings)

def is_ip(word):
    nums = word.split(".")
    if (len(nums) != 4):
        return False
    for num in nums:
        try:
            x = int(num)
        except:
            return False
    return True

# doing nslookup and ping on hostnames & ips

# gets string word which is IP address or hostname 
# and returns hostname or IP that resulted from `nslookup {word}`
def nslookup(word):
    input_is_hostname = is_hostname(word)
    filename = 'test.txt'
    os.system('nslookup ' + word + ' > ' + filename) 
    
    file = open(filename)
    lines = file.readlines()
    num_lines = len(lines)
    
    # looked up hostname
    if (input_is_hostname):
        # lookup returned 'No answer'
        if (num_lines < 7):
            return no_answer
        # lookup was successful
        for i in range(5, 7):
            words = lines[i].split(": ")
            if words[0] == ("Address"):
                return words[1].strip("\n")
        return no_answer
    
    # looked up ip
    # ip lookup that returned 'No answer'
    if (num_lines > 15):
        return no_answer
   
    # ip lookup successful
    if (num_lines > 5):
        words = lines[4].split()
        return words[-1][:-1]
    
    # ip lookup not sucessful
    return unfound_dns

# gets string word which is IP address or hostname 
# and returns hostname or IP that resulted from `ping {word}`
def pings(word):
    ping_file = 'test.txt'
    os.system('ping -c 1 ' + word + ' > ' + ping_file)
    file = open(ping_file)
    lines = file.readlines()
    num_packets_line = 3
    if (is_hostname(word)):
        num_packets_line = 4
    if (len(lines) <= 1 or (len(lines) >=3 and lines[3][23:32] == "0 packets")):        
        return False
    return True

# getting comments
def get_nslookup(word):
    if word in dns_records:
        return dns_records[word]
    else:
        lookup_res = nslookup(word)
        dns_records[word] = lookup_res
        dns_records[lookup_res] = word
        return lookup_res
        
def get_ping(word):
    if word in dns_pings:
        return dns_pings[word]
    elif (word == no_answer or word == unfound_dns):
        return True
    else:
        ping_res = pings(word)
        dns_pings[word] = ping_res
        return ping_res

def comment_on_dns(word1=None, word2=None):
    nslookup_comment = ""
    ping_comment = ""
    ip = ""
    hostname = ""
    ip_given = False
    hostname_given = False
    #first input is ip
    if not word1 == None and is_ip(word1):
        ip = word1
        ip_given = True
    #first input is hostname
    if not word1 == None and is_hostname(word1):
        hostname = word1
        hostname_given = True
    #second input is ip
    if not word2 == None and is_ip(word2):
        ip = word2
        ip_given = True
    #second input is hostname
    if not word2 == None and is_hostname(word2):
        hostname = word2
        hostname_given = True
        
    # ip was given
    if ip_given:
        # either getting past nslookup result from dictionary or nslookup now
        lookup_ip_res = get_nslookup(ip)
        # handling nslookup cases
        if (lookup_ip_res == unfound_dns):
            nslookup_comment += "server can't find " + ip + "\n"
        elif (lookup_ip_res == no_answer):
            nslookup_comment += "'No answer' returned for nslookup " + ip + "\n"
        elif (hostname_given and lookup_ip_res != hostname):
            nslookup_comment += ip + " matched with " + lookup_ip_res + "\n"
            
        #either getting past ping result from dictionary or ping now
        if (get_ping(ip) == False):
            ping_comment += ip + " doesn't ping\n"
        if (get_ping(lookup_ip_res) == False):
            ping_comment += lookup_ip_res + " doesn't ping\n"
        
    #hostname was given
    if hostname_given:
        # either getting past nslookup result from dictionary or nslookup now
        lookup_name_res = get_nslookup(hostname)
        # handling nslookup cases
        if (lookup_name_res == no_answer):
            nslookup_comment += "'No answer' returned for nslookup " + name + "\n"
        elif (ip_given and lookup_name_res != ip):
            nslookup_comment += name + " matched with " + lookup_name_res + "\n"
        
        #either getting past ping result from dictionary or ping now
        if not (ip_given and ip == lookup_name_res):
            if (get_ping(hostname) == False):
                ping_comment += hostname + " doesn't ping\n"
            if (get_ping(lookup_name_res) == False):
                ping_comment += lookup_name_res + " doesn't ping\n"
            
    return (nslookup_comment, ping_comment)

## names.csv ##
(names_pd, names_rows, names_num_rows) = pd_rows_len('./csv/names.csv')

name_nslookup_comments = [""]*names_num_rows
name_ping_comments = [""]*names_num_rows

# takes line from names.csv file and returns array of (ip, name)
def parse_name(name):
    ip_name = name[5:].split(" ")
    return (ip_name[0], ip_name[1])

# converting info from names.csv into dictionaries
# and nslook on each IP & host name 
for i in names_rows:
    line = names_pd.loc[i, "Names"]
    print(line)
    (ip, name) = parse_name(line)
    
    (nslookup_c, ping_c) = comment_on_dns(ip, name)
    name_nslookup_comments[i] = nslookup_c
    name_ping_comments[i] = ping_c

names_pd.insert(1, 'nslookup comments', name_nslookup_comments)
names_pd.insert(2, 'ping comments', name_ping_comments)
names_pd.to_csv('./new_csv/new_names.csv')
    
# print_dict(dns_records, "DNS")
# print_dict(dns_pings, "pings")
# print_arr(name_nslookup_comments, "nslookup comments")
# print_arr(name_ping_comments, "ping comments")


## objects.csv

(objects_pd, objects_rows, objects_num_rows) = pd_rows_len('./csv/objects.csv')

objects_nslookup_comments = [""]*objects_num_rows
objects_ping_comments = [""]*objects_num_rows

# takes line from objects.csv file and 
# returns first word (object, host, range, etc) and ip/hostname
def parse_obj_line(object_line):
    words = object_line.split()
    constructor = words[0]
    constructor_arg = ""
    if constructor == "object":
        lastword = words[-1]
        if (lastword[0:3] == "obj"):
            constructor_arg = lastword.split("-")[1]
        else:
            constructor_arg = words[2]
    elif constructor == "subnet" or constructor == "host" or constructor == "range":
        constructor_arg = words[1]
    elif constructor == "network-object":
        if is_ip(words[1]):
            constructor_arg = words[1]
        else:
            constructor_arg = words[2]
    else:
        constructor_arg = None
    return (constructor, constructor_arg)

(buffer, curr_obj_arg) = parse_obj_line(objects_pd.loc[0, "Objects"])
curr_obj_index = 0
curr_host_or_subnet = ""

for i in objects_rows:
    line = objects_pd.loc[i, "Objects"]
    print("\n" + line)
    (constructor, constructor_arg) = parse_obj_line(line)
    
    # handling object cases
    if constructor == "object":
        curr_obj_arg = constructor_arg
        curr_obj_index = i
    
    # handling subnet or host or range cases
    elif constructor == "subnet" or constructor == "host" or constructor =="range":
        curr_attr_arg = constructor_arg
        
        # if parent object and child subnet/host/range has same constructors
        if (curr_obj_arg == curr_attr_arg):
            (nslookup_comment, ping_comment) = comment_on_dns(curr_obj_arg)
            objects_nslookup_comments[curr_obj_index] += nslookup_comment
            objects_ping_comments[curr_obj_index] += ping_comment
        
        # if the parent object and child subnet/host has differing constructors
        # check that they're corresponding IP & name pair
        if (curr_obj_arg != curr_attr_arg):
            (nslookup_comment, ping_comment) = comment_on_dns(curr_obj_arg, curr_attr_arg)
            objects_nslookup_comments[curr_obj_index] += nslookup_comment
            objects_ping_comments[curr_obj_index] += ping_comment
    
    # handling network-object
    elif constructor == "network-object":
        (nslookup_comment, ping_comment) = comment_on_dns(constructor_arg)
        objects_nslookup_comments[i] += nslookup_comment
        objects_ping_comments[i] += ping_comment
    else:
        continue
            
objects_pd.insert(1, 'nslookup comments', objects_nslookup_comments)
objects_pd.insert(2, 'ping comments', objects_ping_comments)
objects_pd.to_csv('./new_csv/new_objects.csv')

# print_dict(dns_records, "DNS")
# print_dict(dns_pings, "pings")
# print_arr(objects_nslookup_comments, "nslookup comments")
# print_arr(objects_ping_comments, "ping comments")


## rules.csv ##
(rules_pd, rules_rows, rules_num_rows) = pd_rows_len('./csv/rules.csv')

# name_comments = ["host names:\n"]*rules_num_rows
# ip_comments = ["IPs:\n"]*rules_num_rows
# rules_comments = [""]*rules_num_rows
rules_nslookup_comments = [""]*rules_num_rows
rules_ping_comments = [""]*rules_num_rows

# returns pair of 2 lists:
# all the names & all the ips in a rule
def parse_rule(rule):
    hostnames = []
    ips = []
    words = rule.split(" ")
    for word in words:
        word = word.strip("(")
        word = word.strip(")")
        if (is_ip(word)):
            ips.append(word)
        if (is_hostname(word)):
            hostnames.append(word) 
    return (ips, hostnames)

for i in rules_rows:
    rule = rules_pd.loc[i, "Rules"]
    print(rule)
    (ips, hostnames) = parse_rule(rule)
    
    for ip in ips:
        (nslookup_comment, ping_comment) = comment_on_dns(ip)
        rules_nslookup_comments[i] += nslookup_comment
        rules_ping_comments[i] += ping_comment
    for hostname in hostnames:
        (nslookup_comment, ping_comment) = comment_on_dns(hostname)
        rules_nslookup_comments[i] += nslookup_comment
        rules_ping_comments[i] += ping_comment
            
rules_pd.insert(1, 'nslookup comments', rules_nslookup_comments)
rules_pd.insert(2, 'ping comments', rules_ping_comments)
rules_pd.to_csv('./new_csv/new_rules.csv')

# print_dict(dns_records, "DNS")
# print_dict(dns_pings, "pings")
# print_arr(rules_nslookup_comments, "nslookup comments")
# print_arr(rules_ping_comments, "ping comments")