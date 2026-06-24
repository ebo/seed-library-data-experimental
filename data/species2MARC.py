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
# This class functionally contains the Library of Congress MARC21
# record definitions.
###############################################################################

###############################################################################
# This generic base class is driven by a combination of the type of
# object being worked on (ctype), and the MARC21 specific mappings
# (from an external CSV file).
###############################################################################

# FIXME: this is a Teriable name.  Need a better one.
class MARC_Record:
    # the LoC MARC21 record fields have the following columns:
    # ["varname","tagfield","liblibrarian","libopac","repeatable","mandatory",
    #  "important","authorised_value","ind1_defaultvalue","ind2_defaultvalue",
    #  "frameworkcode"]
    field = None
    # the LoC MARC21 record subfields have the following columns:
    # ["varname","tagfield","tagsubfield","liblibrarian","libopac","repeatable",
    #   "mandatory","important","kohafield","tab","authorised_value","authtypecode",
    #   "value_builder","isurl","hidden","frameworkcode","seealso","link",
    #   "defaultvalue","maxlength","display_order"]
    subfield = None
    tagfields = []

    def __init__(self, SPF_name):
        # FIXME: need to get the SPF loading correct.
        #    should we pass in the SPF name into init, or 
        self.spf_init(SPF_name)

    # read in and parse the SPF files.
    def spf_init(self, infile):
        with open(infile, mode='r') as spff:
            #########################################################
            # The SPF file is internally semented, and has to be
            # devided into its component parts.  Spin though to find
            # the "#-#" seperated sections, and parse both of them
            # seperately.
            #########################################################
            # FIXME: there should be a better way to do this...
            clines = []
            for l in filter(lambda row: row[0]!='#', spff.readlines()):
                lc = l[0].strip()
                if lc!='#' and lc!='':
                    clines.append(l)

            # FIXME: there should be a better way to do this...
            first = None
            second = None
            for indx,val in enumerate(clines):
                lst = val.split(',')
                if first==None and f'"#-#"' == lst[0]:
                    first = indx
                    continue
                if first!=None and f'"#-#"' == lst[0]:
                    second = indx
                    break

            if first==None or second==None:
                logging.critical(f"SPF file '{infile}' appears to be corrupted.")
                exit(0)

            import pandas as pd
            from io import StringIO

            self.field = pd.read_csv(StringIO('\n'.join(clines[0:first])), dtype=str, keep_default_na=False)
            self.subfield = pd.read_csv(StringIO('\n'.join(clines[first+1:second])), dtype=str, keep_default_na=False)

    # generate a variable name from a mapping.  This roughly =
    #    <tag>|<subtag>|<var>
    def __gen_name__(self, dct):
        ret = None
        try:
            # for all subfields
            ret = '|'.join([str(dct['tagfield'].values[0]),
                             str(dct['tagsubfield'].values[0]),
                            str(dct['varname'].values[0])])
            logger.debug(f"gen_name = {ret}")
        except:
            try:
                # for all fields
                ret = '|'.join([str(dct['tagfield'].values[0]),
                                str(dct['varname'].values[0])])
                logger.debug(f"gen_name(2) = {ret}")
            except Exception as ex:
                logging.exception(f"{ex}")
                
        return ret

    # decode the '|' concatened name.
    def __decode_name__(self, name):
        [dt,ds,dv] = name.split('|')
        return dt,ds,dv
    
    # set the key/value pair as a class variable.
    def set(self, var, val):
        # find the single unique entry with the variable name.
        #
        # if there are none, then you have a typo and calling
        # something not in this SPF.
        #
        # if there are multiple returns, then there is a failat error
        # in the SPF definitions.
        try:
            dct = self.subfield[self.subfield['varname']==var]
        except Exception as e:
            logging.exception(f"self.subfield failed.\n\n**** Probably forgot to load the SPF definitions.\n\n")
            exit(-1)
            return
        
        dl = len(dct)

        if 1 == dl:
            # Generate a database name from the map structure.
            setattr(self, self.__gen_name__(dct), val)
            self.tagfields.append(dct["tagfield"])
        elif 0 == dl:
            # No name was found. skip and warn about bad name or typo
            logger.warning(f"variable '{var}' not found.")
        else:
            # Multiple map entries found.  Post error to repair mappings.
            logger.error(f"variable '{var}' returns more than one mapping.")
            logger.error(f"  repair mappings file entries:")
            for d in dct:
                logger.error(f"    {d}")

        return

    def __str__(self):
        return ', '.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))])

    def __repr__(self):
        return "".join([f"{self.ctype}(",','.join([f"{k}:'{getattr(self, k)}'" for k in list(vars(self))]),")"])

    # MARC21 converts the variable mappings to a MARC21 record.
    def MARC21(self):
        from pymarc import Record, Field, Subfield, MARCWriter, MARCReader
        import io
        #global mappings
        
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

        # set a date version number
        # FIXME: find a way to set this externally.
        self.set("version", "0.1")
        self.set("version_auth", "Koha_Seed")

        # iterate through the tags and find all set
        for t in sorted(set([str(t.values[0]) for t in self.tagfields])):
            logger.debug(f"processing field: '{t}':")
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

            # I still need to find and extract the indicators
            fld = self.field[self.field["tagfield"]==t]
            ind1 = fld["ind1_defaultvalue"].values[0]
            ind2 = fld["ind2_defaultvalue"].values[0]
            if ''==ind1: ind1 = " "
            if ''==ind2: ind2 = " "
            
            logging.debug(f"  * ind1='{ind1}'  ind2='{ind2}'")
            
            # construct the rew record.
            record.add_field(
                Field(
                    tag=str(t),
                    indicators=[ind1,ind2],
                    subfields=nsubfields
                )
            )
            
        # convert the record to a human readable form
        trec = '\n'.join([str(r) for r in MARCReader(record.as_marc())])
        return trec

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
        # FIXME: need to rework the checker...
        return ret

        required = [self.__gen_name__(itm) for itm in self.subfield if itm["mandatory"]=="True" and itm["class"]==self.ctype]
        my_vars = list(vars(self))
        
        for k in required:
            if k not in my_vars:
                ret = False
                logger.error(f"Required variable '{k}' not in '{self.ctype}' object")
        return ret

# the Species class covers the biographic analogy of species <=> author.
class Species (MARC_Record):
    def __init__(self, SPF_name):
        super().__init__(SPF_name)
        self.ctype = "Species"

# the Collection class covers the bibliographic analogy of species <=>
# books/events and serial publications.
class Collection (MARC_Record):
    def __init__(self, SPF_name):
        super().__init__(SPF_name)
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
                        #default=None,
                        default=f"{os.path.splitext(prog)[0]}.log",
                        help="Output log filename (default: %(default)s)")
    parser.add_argument("-S","--spffile", type=str, required=False,
                        default="./seed_SPF.csv",
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
    logging.addLevelName(logging.DEBUG,    "DEB")
    logging.addLevelName(logging.INFO,     "INF")
    logging.addLevelName(logging.WARNING,  "WRN")
    logging.addLevelName(logging.ERROR,    "ERR")
    logging.addLevelName(logging.CRITICAL, "CRT")

    # read in the 
    #spf = SPF(args.spffile)
    
    # convert the CSV table into a mappings array of dictionarys.
    #global mappings
    #with open(args.mapfile, mode='r') as mp:
    #    import csv
    #    
    #    # Create a DictReader object (ignoring any comments)
    #    reader = csv.DictReader(filter(lambda row: row[0]!='#', mp))
    # 
    #    # Convert the reader object into a list of dictionaries
    #    mappings = [row for row in reader]

    # simple test of a species I am interested in
    s = Species(args.spffile)
    #s.spf_init()
    s.set("full_name","Sanguinaria canadensis L.")
    s.set("common_name","bloodroot")
    #s.set("species_id","urn:usda:saca13")
    s.set("species_id","saca13")
    s.set("source","plantsdb")
    s.set("link","https://www.loc.gov/standards/sourcelist/taxonomic.html")
    ####s.set("auxilary_info","This is a JSON load test.")
    #s.set("auxilary_data",{"name":"test","var":"woof"})

    # check to make sure that all required variables are set
    logger.info(f"check all required fields set: {s.check_required()}")

    # process the record and write the MARC21 record to the log file
    # if in debug or verbose logging mode.
    record = s.MARC21()
    logger.info("") # add blank lines around the record
    logger.info("record:")
    for l in record.split('\n'):
        logger.info(f"   {l}")
    # diagnostic output for testing.
    print(f"\n{record}")
        
