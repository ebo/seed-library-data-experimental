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

map = [ # Species level tags (analogous to author)
        #   also look at 600 - SUBJECT ADDED ENTRY--PERSONAL NAME
        #                650 - SUBJECT ADDED ENTRY--TOPICAL TERM
        #                651 - SUBJECT ADDED ENTRY--GEOGRAPHIC NAME
        #                657 - INDEX TERM--FUNCTION
        {"required":True, "class":"Species","tag":100,"subtag":"$a","var":"name"},
        {"required":False,"class":"Species","tag":100,"subtag":"$c","var":"common"}, 
        {"required":False,"class":"Species","tag":100,"subtag":"$g","var":"germination"},
        {"required":False,"class":"Species","tag":100,"subtag":"$j","var":"growth_form"},
        # part/number?
        {"required":False,"class":"Species","tag":100,"subtag":"$q","var":"full_name"},
        # veg class is a 
        {"required":False,"class":"Species","tag":100,"subtag":"$u","var":"veg_class"},

        {"required":False,"class":"Species","tag":100,"subtag":"$0","var":"urn"},
        {"required":False,"class":"Species","tag":100,"subtag":"$1","var":"species_id"},
        # define difference between link, field link and others.
        {"required":False,"class":"Species","tag":100,"subtag":"$6","var":"link"},
        {"required":False,"class":"Species","tag":100,"subtag":"$8","var":"field_link"},

        # 210: abbreviated titles.  This might work for encodings (eg. USDA:SACA13)

        # 504: Bibliography, etc. Note

        # 506: *** Restriction on Access Note

        # 508: creation/production credit notes: crediting people who did operations?

        # 514: Data Quality Note: this might work for QA/QC and
        #        germination rate tracking for seed-banks.

        # 516: computer file/data record - for experiments, notes, etc.

        # 518: date/time and place of an event note: not sure how this
        #        compares with other dates/times above

        # 520: Summary...

        # 522: *** Geographic Coverage Note: used to describe native range or other info

        # 542: copyright status if there is one <==> patented or other limitation

        # 545: Biographical or Historical Data: history notes?  How about enthobotony?

        ###############################################################################
    
        # collections levels (analogous to ????)
        {"required":False,"class":"Collection","tag":110,"subtag":"$a","var":"name"},
        {"required":True, "class":"Collection","tag":110,"subtag":"$0","var":"id"},
        # define difference between link, field link and others.
        {"required":False,"class":"Collection","tag":110,"subtag":"$6","var":"link"},
        {"required":False,"class":"Collection","tag":110,"subtag":"$8","var":"field_link"},

        # 048: has preformer <==> collector (is recurring)
        # 382: medium of performance looks  like it might work for an event
        # 384: Key -- how does this compare to species names and identifiers?
        # 386: Creator/Contributor -- collection events and people?
        # 387: REPRESENTATIVE EXPRESSION CHARACTERISTICS: could this work for experiments and grow outs?
        # 388: Time Period of Creation: might work as a general tool for (re)packaging
        # 400: possibly (sub)collections and splitting into packets, etc.
        # 410: Meeting Name?  How should this be used?  Just as a regular meetings?

        # 500/501: Notes: when should I sue them?

        # 535: Location of Originals/Duplicates Note: where are the materials housed?

        # 541: Immediate Source of Acquisition Note: how was it aquired (gift, purchase, wildcraft)

        # 561: Ownership and Custodial History: needed for provenance of source and care.

        # 567: Methodology Note: collection technique, treatment, storage or other processing.

        # 583: Action Note: for just about any event (including experiments)

        # 648: Subject Added Entry--Chronological Term: need time and
        #        duration stamps for things.  Is this the best way?

        # 852 - Location

        ###############################################################################
    
        # 526: Study Program Information Note: scientific study?
      ]

# The species class
# FIXME: most of the functions are common, define a base class and inherit -- and use the ctype
class Taxonomy:
    ctype = None

    def __init__(self):
        return
        
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
        required = [itm["var"] for itm in map if itm["required"]==True and itm["class"]==self.ctype]
        my_vars = list(vars(self))

        for k in required:
            if k not in my_vars:
                ret = False
                print(f"Error: Required variable '{k}' not in '{self.ctype}' object")
        return ret

class Species (Taxonomy):
    def __init__(self):
        self.ctype = "Species"
        return


class Collection (Taxonomy):
    def __init__(self):
        self.ctype = "Collection"
        return

s = Species()
s.set("name","Sanguinaria canadensis L.")
s.set("urn","urn:usda:saca13")
s.set("common","bloodroot")

print(s)
print(repr(s))

print("check:",s.check_required())
exit(0)
