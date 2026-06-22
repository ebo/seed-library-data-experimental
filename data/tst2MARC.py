#!/usr/bin/env python

# FIXME: this is a test of some infrastructure to see how it
#   behaves. It is intended for experimental purposes only.

import os,sys
import pymarc

###############################################################################
# this is a collection of class:variable/value substitutions to MARC21 tags.
#
# FIXME: I probably will not be able to use a simple class/dict for
#        entries that can take multiple copies of a particular tag.
#        Need to refactor code to support.
###############################################################################

# The generic base class.  Most functions have been refactored to
# trigger off of the ctype variable, which is set in the derived
# classes below.
#
# This generic base class is driven by a combination of the type of
# object being worked on (ctype), and the MARC21 specific mappings (in
# a provided CSV file).

# FIXME: this is a Teriable name.  Need a better one.
class Taxonomy:
    def __init__(self):
        # FIXME: define the version number/string as part of the
        #        external project configuration.
        # set the version number - set for all classes.
        self.set("version", "0.1")

    # generate a variable name from a mapping.  This roughly =
    #    <tag>|<subtag>|<var>
    def __gen_name__(self, dct):
        return '|'.join([dct['tag'],dct['subtag'],dct['var']])

    # decode the '|' concatened name.
    def __decode_name__(self, name):
        [dt,ds,dv] = name.split('|')
        return dt,ds,dv
    
    # set the key/value pair as a class variable.
    def set(self, var, val):
        global mappings
        # find the single unique entry with the variable name
        dct = [d for d in mappings if d['var']==var]
        #print(f"count: '{len(dct)}'")
        #print(f"map entry: '{dct}'")
        setattr(self, self.__gen_name__(dct[0]), val)
        return

    def __str__(self):
        return ', '.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))])

    def __repr__(self):
        return "".join([f"{self.ctype}(",','.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))]),")"])

    # MARC21 converts the variable mappings to a MARC21 record.
    def MARC21(self):
        from pymarc import Record, Field, Subfield, MARCWriter, MARCReader
        import io
        global mappings
        
        record = Record()

        # 2. Add control fields (tags under 010 do not use indicators
        #    or subfields)
        # FIXME: how did they determine the data value here?
        record.add_field(
            Field(tag='001', data='ocm01234567')
        )

        # iterate through the tags and find all set
        for t in sorted(set([itm['tag'] for itm in mappings])):
            print(f"processing tag '{t}':")
            nsubfields = []
            for itm in list(vars(self)):
                try:
                    dt,ds,dv = self.__decode_name__(itm)
                except:
                    continue
                
                if dt == t:
                    v = getattr(self,itm)
                    #print(f" ... {dt,ds,dv} = {v}")
                    nsubfields.append(Subfield(code=ds, value=v))
                    #print(f"tag={dt}  type={type(dt)}")
                    #print(f"subtag={ds}  type={type(ds)}")
                    #print(f"var={dv}  type={type(dv)}")
                    #print(f"value={v}  type={type(v)}")
                    #print("")
                    
            record.add_field(
                Field(
                    tag=str(t),
                    # FIXME: where should I get/set indicators?
                    indicators=['1', ' '],
                    subfields=nsubfields
                )
            )
            
        # 4. Save the record to a binary MARC (.mrc) file
        #with open('output_records.txt', 'w', encoding='utf-8') as file_handler:
        if False:
            # write out record in binary form
            with open('output_records.txt', 'wb') as file_handler:
                writer = MARCWriter(file_handler)
                writer.write(record)
                writer.close()
                return
        elif False:
            # return binary string represnetation of the record
            mstream = io.BytesIO()
            writer = MARCWriter(mstream)
            writer.write(record)
        
            marc_string = mstream.getvalue().decode('utf-8')
            print(marc_string)
            writer.close()
            return marc_string
        else:
            # convert the record to a human readable form
            trec = '\n'.join([str(r) for r in MARCReader(record.as_marc())])
            return trec

        # Example: Species (Author) Main Entry (100)
        #subfields = self.getsubfields(self, tag=100
        #record.add_field(
        #    Field(
        #        tag='100',
        #        indicators=['1', ' '],
        #        subfields=[
        #            Subfield(code='a', value='Thomas, David,'),
        #            Subfield(code='e', value='species.')
        #        ]
        #    )
        #)

        
    # check_required is a simple consistency check to ensure that all
    # required arguments are included.  Returns True if OK and False
    # otherwise (with simple error messages of what is missing).
    # FIXME: need to migrate error messages into proper logging.
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
        super().__init__()
        self.ctype = "Species"

# the Collection class covers the bibliographic analogy of species <=>
# books/events and serial publications.
class Collection (Taxonomy):
    def __init__(self):
        super().__init__()
        self.ctype = "Collection"

###############################################################################

if __name__ == "__main__":
    map_file = "mappings_v0.1.csv"

    # convert the CSV table into a mappings array of dictionarys.
    global mappings
    with open(map_file, mode='r') as mp:
        import csv
        
        # Create a DictReader object (ignoring any comments)
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
        s.set("sp_name","Sanguinaria canadensis L.")
        s.set("urn","urn:usda:saca13")
        s.set("common","bloodroot")
        
    if False:
        print(s)
        print(repr(s))

        print("check:",s.check_required())

    if True:
        ret = s.MARC21()
        print("record:")
        print(ret)
        
    if False:
        from pymarc import Record, Field, Subfield, MARCWriter

        # 1. Initialize a new blank MARC record
        record = Record()

        # 2. Add control fields (tags under 010 do not use indicators
        #    or subfields)
        record.add_field(
            Field(tag='001', data='ocm01234567')
        )

        
        # 3. Add variable data fields using Subfield objects
        # Example: ISBN (020)
        record.add_field(
            Field(
                tag='020',
                indicators=[' ', ' '],
                subfields=[
                    Subfield(code='a', value='9780135957059')
                ]
            )
        )

        # Example: Author Main Entry (100)
        record.add_field(
            Field(
                tag='100',
                indicators=['1', ' '],
                subfields=[
                    Subfield(code='a', value='Thomas, David,'),
                    Subfield(code='e', value='author.')
                ]
            )
        )
        
        # Example: Title Statement (245)
        record.add_field(
            Field(
                tag='245',
                indicators=['1', '4'],  # Ind 2 = 4 ignores "The " when indexing/sorting
                subfields=[
                    Subfield(code='a', value='The pragmatic programmer : '),
                    Subfield(code='b', value='your journey to mastery / '),
                    Subfield(code='c', value='David Thomas, Andrew Hunt.')
                ]
            )
        )

        # Example: Publication Information (264 / 260)
        record.add_field(
            Field(
                tag='264',
                indicators=[' ', '1'],
                subfields=[
                    Subfield(code='a', value='Boston : '),
                    Subfield(code='b', value='Addison-Wesley, '),
                    Subfield(code='c', value='2020.')
                ]
            )
        )

        # 4. Save the record to a binary MARC (.mrc) file
        with open('output_records.mrc', 'wb') as file_handler:
            writer = MARCWriter(file_handler)
            writer.write(record)
            writer.close()
            
        print("MARC record successfully created and saved.")
