#!/usr/bin/env python

# FIXME: this is a test of some infrastructure to see how it
#   behaves. It is intended for experimental purposes only.

import os,sys

###############################################################################
# this is a collection of class:variable substitutions to MARC21 tags.
# FIXME: define a tag for the version accession number -- used for data migration (538?)
# FIXME: probably need to add something for when you can have more than 1 0=>not required?
# FIXME: I probably will not be able to use a simple class/dict for
#        entries that can take multiple copies of a particular tag.
#        Need to refactor code to support.
###############################################################################
# FIXME: refactor the mappings below to read in a CSV file with the entries in them.
###############################################################################

# Note: mappings has been refactored to be CSV file driven.
# mappings = [ # Species level tags (analogous to author)...


# The generic base class.  Most functions have been refactored to
# trigger off of the ctype variable, which is set i nthe deerived
# classes below.
#
# This generic base class is driven by a combination of the type of
# object being worked on (ctype), and the MARC21 specific mappings (in
# a provided CSV file).

# FIXME: this is a Teriable name.  Need a better one.
class Taxonomy:
    def __init__(self):
        self.ctype = None
        
    def set(self, var, val):
        setattr(self, var, val)
        return

    def __str__(self):
        return ', '.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))])

    def __repr__(self):
        return "".join([f"{self.ctype}(",','.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))]),")"])

    def MARC21(self):
        print(f"{self.ctype} MARC21:",self.keys())

    def check_required(self):
        ret = True
        required = [itm["var"] for itm in mappings if itm["required"]==True and itm["class"]==self.ctype]
        my_vars = list(vars(self))

        for k in required:
            if k not in my_vars:
                ret = False
                print(f"Error: Required variable '{k}' not in '{self.ctype}' object")
        return ret

# the Species class covers the biographic analogy of species <=> author.
class Species (Taxonomy):
    def __init__(self):
        self.ctype = "Species"

# the Collection class covers the bibliographic analogy of species <=>
# books/events and serial publications.
class Collection (Taxonomy):
    def __init__(self):
        self.ctype = "Collection"

###############################################################################

if __name__ == "__main__":
    map_file = "mappings_v0.1.csv"

    # convert the CSV table into a mappings array of dictionarys.
    global mappings
    with open(map_file, mode='r') as mp:
        import csv
        
        # Create a DictReader object
        reader = csv.DictReader(filter(lambda row: row[0]!='#', mp))
    
        # Convert the reader object into a list of dictionaries
        mappings = [row for row in reader]

    if False:
        # debug write: the map file 
        for itm in mappings:
            for k in itm:
                print(f"{k}: {itm[k]}")
            print("")
    
    if True:
        # simple test of a species I am interested in
        s = Species()
        s.set("name","Sanguinaria canadensis L.")
        s.set("urn","urn:usda:saca13")
        s.set("common","bloodroot")
        
        print(s)
        print(repr(s))

        print("check:",s.check_required())



