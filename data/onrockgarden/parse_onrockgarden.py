#!/usr/bin/env python

import os,sys
import pandas as pd
import io

ifname = "view-source_https___onrockgarden.com_index.php_germination-guide_germination-guide.html"

def clean(l):
    l = str(l.strip())
    l = l.replace("&deg;","")
    return l

def extract_var(l,row):
    l = clean(l)
    if ("data-child-value" in l):
        i = l[53:-9].strip()
        row = i
    if ("<td align=\"center\">" in l):
        i = l[21:-6].strip()
        row = row + '|' + i
    if ("<td><a " in l):
        p = l[10:].find("_blank")+8
        i = l[p+10:-10].strip()
        row = row + '|' + i
    return row

def extract_line(lines):
    p = 0
    try:
        l = clean(lines[p])
    except:
        return (lines[p+1:],"")
    
    item = []
    row = []
    if ("<tr data-child-value=" in l):
        #print("found!")
        row = extract_var(l+clean(lines[p+1]),row)
        p = p +1
        while "</tr>" not in l:
            p = p +1
            l = clean(lines[p])
            item.append(l)
            #print("=>:",l)
            row = extract_var(l,row)
        return (lines[p:],row)
    return (lines[p+1:],"")

header = "details|name|viable|germ_code|mod1|mod2|mod3|mod4|special_info"
parsed = [header]
with open(ifname,'br') as fin:
    lines = fin.readlines()
    while lines != []:
        (lines,row) = extract_line(lines)
        if (row != ""):
            parsed.append(row)
            #print(row)

print(parsed)
print("*****: done parsing")
csv_string = "\n".join(parsed)
print("*****: done join")
data_io = io.StringIO(csv_string)
print("*****: done StringIO")
df = pd.read_csv(data_io,sep='|',dtype={'mod1': str, 'mod2': str,
                                        'mod3': str, 'mod4': str})
print("*****: done reading")

print(df)
print("*****: done print")
df.to_csv("onrockgarden.csv", sep='|', index=False)
