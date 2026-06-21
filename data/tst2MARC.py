#!/usr/bin/env python

# FIXME: this is a test of some infrastructure to see how it
#   behaves. It is intended for experimental purposes only.

import os,sys
#import pymarc
#import pandas as pd
#import numpy as np

# this is a collection of class:variable substitutions to MARC21 tags.
map = [ # Species level tags (analogous to author)
        {"required":True,"class":"Species","var":"name","tag":100,"subtag":"$a"},
        {"required":False,"class":"Species","var":"common","tag":100,"subtag":"$b"}, 
        {"required":True,"class":"Species","var":"urn","tag":100,"subtag":"$u"},

        # collections levels (analogous to ????)
      ]

# The species class 
class Species:
    def __init__(self, name, urn, common=None):
        self.name = name
        self.urn = urn
        if common is not None:
            self.common = common

    def set(self, var, val):
        setattr(self, var, val)
        return

    def __str__(self):
        return ', '.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))])

    def __repr__(self):
        return "".join(f"Species("','.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))]),")")

    def MARC21(self):
        print("Species MARC21:",self.keys())

    def check_required(self):
        ret = True
        required = [itm["var"] for itm in map if itm["required"]==True]
        my_vars = list(vars(self))

        for k in required:
            if k not in my_vars:
                ret = False
                print(f"Error: Required variable '{k}' not in species object")
        return ret

class Collection:
    def __init__(self, name, urn):
        self.name = name
        self.urn = urn

    def set(self, var, val):
        return

    def __str__(self):
        return f"name:'{self.name}' urn:'{self.urn}'"

    def __repr__(self):
        return f"Species(name='{self.name}', urn='{self.urn}'"


s = Species("Sanguinaria canadensis L.","urn:usda:saca13")
s.set("common","bloodroot")
for k in list(vars(s)):
    print("  : ",k)

print(s)
print("check:",s.check_required())
exit(0)
