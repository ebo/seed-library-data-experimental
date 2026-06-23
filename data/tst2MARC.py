#!/usr/bin/env python

# FIXME: this is a test of some infrastructure to see how it
#   behaves. It is intended for experimental purposes only.

###############################################################################
# this is a collection of class:variable/value substitutions to MARC21 tags.
#
# FIXME: I probably will not be able to use a simple class/dict for
#        entries that can take multiple copies of a particular tag.
#        Need to refactor code to support.
###############################################################################

import os,sys
import pymarc
from datetime import datetime
import json

# uuid7 (time-ordered) unique ID's are built in as of python-3.14+
if sys.version_info < (3, 14):
    import uuid_utils as uuid

###############################################################################
# logging handlers
###############################################################################
import logging
logger = logging.getLogger(__name__)

###############################################################################

# The generic base class.  Most functions have been refactored to
# trigger off of the ctype variable, which is set in the derived
# classes below.
#

###############################################################################
# This generic base class is driven by a combination of the type of
# object being worked on (ctype), and the MARC21 specific mappings
# (from an external CSV file).
###############################################################################

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
        dl = len(dct)

        if 1 == dl:
            # Generate a database name from the map structure.
            setattr(self, self.__gen_name__(dct[0]), val)
        elif 0 == dl:
            # No name was found. skip and warn about bad name
            # FIXME: convert to proper logging
            logger.warn(f" variable '{var}' not found.")
        else:
            # Multiple map entries found.  Post error to repair mappings.
            # FIXME: convert to proper logging
            logger.error(f" variable '{var}' returns more than one mapping.")
            logger.error(f"   repair mappings file entries:")
            for d in dct:
                logger.error(f"     {d}")

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

        # Add control fields (tags under 010 do not use indicators
        #    or subfields)
        #
        # unique record ID. Generated with a time-orded UUID
        # FIXME: uuid_utils is needed for python-3.13 or older.
        #        python-3.14+ comes with uuid7 built in
        nuid = uuid.uuid7()
        record.add_field(Field(tag='001', data=nuid))

        #  control number identifier
        record.add_field(Field(tag='003', data='Koha-Seed'))

        #  date/time of record creation
        record.add_field(Field(tag='005', data=datetime.now().strftime("%Y%m%d%H%M%S.%f")[:-4]))

        # iterate through the tags and find all set
        for t in sorted(set([itm['tag'] for itm in mappings])):
            logger.debug(f" processing field: '{t}':")
            nsubfields = []
            for itm in list(vars(self)):
                try:
                    dt,ds,dv = self.__decode_name__(itm)
                except:
                    # this is expected for "ctype" and onter simple
                    # varlables.  You can safely ignore it.
                    continue
                
                if dt == t:
                    v = getattr(self,itm)
                    nsubfields.append(Subfield(code=ds, value=v))
                    
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
            logger.debug(marc_string)
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

    # Auxilary data (in the firm of fields 980 and 990) are saved as a
    # JSON load converted from a python dictionary object.
    def gen_aux_data(self, dct):
        data = json.dumps(dct)
        return data
    
    # check_required is a simple consistency check to ensure that all
    # required arguments are included.  Returns True if OK and False
    # otherwise (with simple error messages of what is missing).
    def check_required(self):
        ret = True
        required = [self.__gen_name__(itm) for itm in mappings if itm["required"]=="True" and itm["class"]==self.ctype]
        my_vars = list(vars(self))
        
        for k in required:
            if k not in my_vars:
                ret = False
                logger.error(f" Required variable '{k}' not in '{self.ctype}' object")
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
    import argparse

    prog = os.path.basename(__file__) # os.path.basename(sys.executable)
    
    parser = argparse.ArgumentParser(prog=prog, description="Convert a Species or Seed Collection to a MARC21 record (experimental testing).")

    parser.add_argument("-i","--infile", type=str, required=True,
                        help="The input species/collection file (required)")
    parser.add_argument("-m","--mapfile", type=str, required=False,
                        default="./mappings_v0.1.csv",
                        help="The MARC21 mappings file (default: %(default)s)")
    parser.add_argument("-L","--logfile", type=str, required=False,
                        default=None,
                        help="Output log filename (default: %(default)s)")
   
    parser.add_argument("-l", "--log", default='WARNING', required=False,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: %(default)s)')
    
    args = parser.parse_args()

    # set the log levels, and logging to external file if desired.
    FORMAT = '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    logging.basicConfig(level=args.log,handlers=[logging.StreamHandler()],
                        format=FORMAT)
    if args.logfile is not None:
        file_handler = logging.FileHandler(args.logfile, mode="w",
                                           encoding="utf-8", delay=True)
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(fmt=FORMAT)
        
        file_handler.setLevel(args.log)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # convert the CSV table into a mappings array of dictionarys.
    global mappings
    with open(args.mapfile, mode='r') as mp:
        import csv
        
        # Create a DictReader object (ignoring any comments)
        reader = csv.DictReader(filter(lambda row: row[0]!='#', mp))
    
        # Convert the reader object into a list of dictionaries
        mappings = [row for row in reader]

    # simple test of a species I am interested in
    s = Species()
    s.set("full_name","Sanguinaria canadensis L.")
    s.set("common_name","bloodroot")
    #s.set("species_id","urn:usda:saca13")
    s.set("species_id","saca13")
    s.set("source","plantsdb")
    s.set("link","https://www.loc.gov/standards/sourcelist/taxonomic.html")
    s.set("auxilary_info","This is a JSON load test.")
    s.set("auxilary_data",{"name":"test","var":"woof"})

    # check to make sure that all required variables are set
    logger.debug(f" check all required fields set: {s.check_required()}")

    print("")
    print(s.MARC21())
        
