#!/usr/bin/env python

import os,sys
import pymarc
import pandas as pd
import numpy as np

def find_row_symbol_other (df, symbol1, value, symbol2):
    dr = df[df[symbol1].str.contains(value)]
    print(dr)

    #return dr[dr[symbol2]][0]

def find_row_symbol (df, symbol, value):
    dr = df[df[symbol].str.contains(value)]
    return dr

fname1 = "USDA_checklist_clean.csv"
fname2 = "onrockgarden.csv"

binomial = "Sanguinaria canadensis"

# USDA Plant ID
df1 = pd.read_csv(fname1,sep=',')

dr1 = df1["Scientific_Name_with_Author"]
#dr1 = df1[df1["Scientific_Name_with_Author"].str.contains(binomial)]
print(dr1,"\n")
idx = pd.Index(dr1)
na_mask = idx.isna()
print("na_mask:",dr1[dr1.isna()].index.tolist())

#print(dr1.head(),"\n")

#dr1 = find_row_symbol_other (df1, "Scientific Name with Author", binomial, "Symbol")
#dr1 = find_row_symbol (df1, "Scientific Name with Author", binomial)
#print(dr1.head(),"\n")


# onrockgarden
if False:
    df2 = pd.read_csv(fname2,sep='|',dtype={'mod1': str, 'mod2': str,
                                            'mod3': str, 'mod4': str})
    dr2 = find_row_symbol (df2, "name", binomial)
    print(dr2.head(),"\n")




#filtered = df1[df1['mod4'].notna()]
#print(filtered.head(n=1))

#df2 = pd.read_csv(fname2,sep='|')
#print(df2.head(n=1),"\n")
