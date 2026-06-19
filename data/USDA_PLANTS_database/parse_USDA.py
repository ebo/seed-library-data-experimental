#!/usr/bin/env python

import os,sys
import pymarc
import pandas as pd
import numpy as np

fname1 = "USDA_checklist.csv"
fname2 = "USDA_checklist_clean.csv"


# clean up the USDA plant ID list.
# remove anything that does not contain a scientific name.
# remove any that have a Synonym_Symbol (these are old names)

# USDA Plant ID
df1 = pd.read_csv(fname1, sep=',', dtype=str)

#dr1 = df1["Scientific_Name_with_Author"]
#dr1 = df1[df1["Scientific_Name_with_Author"]!=""]
dr1 = df1[df1["Synonym_Symbol"]==""]

#dr1.to_csv(fname2, sep=',')


print(dr1,"\n")
