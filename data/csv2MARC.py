#!/usr/bin/env python

import os,sys
import pymarc
import pandas as pd
import numpy as np

fname1 = "onrockgarden.csv"
fname2 = "BRAHMS_specimins1.csv"
fname3 = ""

df1 = pd.read_csv(fname1,sep='|',dtype={'mod1': str, 'mod2': str,
                                        'mod3': str, 'mod4': str})
print(df1.head(n=1),"\n")

#filtered = df1[df1['mod4'].notna()]
#print(filtered.head(n=1))

df2 = pd.read_csv(fname2,sep='|')
print(df2.head(n=1),"\n")
