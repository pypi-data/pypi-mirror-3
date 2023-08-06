#!/usr/bin/env python
'''
pyinspire - command line retrieval of INSPIRE HEP database results
Author: Ian Huston
Released under the modified BSD license.

Example: pyinspire.py -b -s "find a Feynman, Richard"
'''
import sys
import urllib
from bs4 import BeautifulSoup
import optparse
import logging

__version__ = "0.1.2"
APIURL = "http://inspirehep.net/search?" 
logging.basicConfig()
log = logging.getLogger("pyinspire")
 

def get_text_from_inspire(search="", resultformat="brief"):
    """Extract text from an INSPIRE search."""
    log.info("Search of INSPIRE started...")
    data = query_inspire(search, resultformat=resultformat)
    text = extract_from_data(data)
    return text

def query_inspire(search="", resultformat="brief"):
    """Query the INSPIRE HEP database and return the entries.

    Parameters
    ----------
    search : string
             search string to use in query

    resultformat : string
             long hand name of format, ["brief", "bibtex", "latexEU", "latexUS"]

    """
    formats = {"brief": "hb",
               "bibtex": "hx",
               "latexEU": "hlxe",
               "latexUS": "hlxu"}
    inspireoptions = dict(action_search="Search",
                          rg=100, #number of results to return in one page
                          of=formats[resultformat], # format of results 
                          ln="en", #language
                          p=search # search string
                          )
    
    url = APIURL + urllib.urlencode(inspireoptions)
    log.debug("Query URL is %s", str(url))
    
    try:
        f = urllib.urlopen(url)
        log.debug("Starting to read data from %s.", str(url))
        data = f.read()
        log.debug("Data has been read: \n %s", str(data))
    except IOError, e:
        log.error("Error retrieving results: %s", str(e))
        raise
    return data
    
def extract_from_data(data):
    soup = BeautifulSoup(data)
    
    if soup.pre:
        text = extract_pre_tags(soup)
    else:
        text = extract_text(soup)
    
    return text

def extract_pre_tags(soup):
    """Extract text from <pre> tags in BeautifulSoup soup."""
    text = "\n".join([tag.text for tag in soup.find_all("pre")])
    return text
    
def extract_text(soup):
    """Extract useful text from BeautifulSoup soup"""
    mainbodies = soup.find_all("div", {"class":"record_body"})
    moreinfos = soup.find_all("div", {"class":"moreinfo"})
    if len(mainbodies) != len(moreinfos):
        raise ValueError("Number of records is inconsistent.")
    if len(mainbodies) == 0:
        log.info("No useful information found in text.")
        return ""
    [t.small.ul.replaceWith("") for t in mainbodies if t.small.ul]  
    moreinfotext = [mi.text.replace("Detailed record - ", "") for mi in moreinfos]
    ts = [mb.text + "\n" + mi for mb, mi in zip(mainbodies, moreinfotext) ]
    text = ("\n"+40*"="+"\n").join(ts).replace("\n\n", "\n")
    return text

def main(argv=None):
    """ Main method to deal with command line arguments.

    """
    if not argv:
        argv = sys.argv
    #Parse command line options
    usage = "%prog [options] -s \"INSPIRE search string\"\n" + __doc__
    parser = optparse.OptionParser(usage=usage, version=__version__)
            
    parser.add_option("-s", "--search", action="store", dest="search",
                      type="string", 
                      metavar="STRING", help="search string to send to INSPIRE")
    
    parser.add_option("-b", "--bibtex", action="store_const", 
                      dest="resultformat", const="bibtex", default="brief",
                  help="output bibtex for entries")
    parser.add_option("--latexEU", action="store_const", 
                      dest="resultformat", const="latexEU",
                  help="use LaTeX(EU) format for entries")
    parser.add_option("--latexUS", action="store_const", 
                      dest="resultformat", const="latexUS",
                  help="output bibtex for entries")
    parser.add_option("-v", "--verbose",
                  action="store_const", const=logging.INFO, dest="loglevel",
                  help="print informative messages", default=logging.INFO)
    parser.add_option("--debug",
                  action="store_const", const=logging.DEBUG, dest="loglevel",
                  help="log lots of debugging information")
            
    (options, args) = parser.parse_args(args=argv[1:])
    
    log.setLevel(options.loglevel)
    log.debug("pyinspire called with the following options:\n %s", str(options)) 

    try:
        result = get_text_from_inspire(options.search, options.resultformat)
        log.debug("Successfully extracted text from search.")
        print(result)
    except Exception, e:
        log.error("Error during retrieval of results: %s", str(e))
        return 1
    log.debug("Successfully exited.")
    return 0
    
        


if __name__ == "__main__":
    sys.exit(main(sys.argv))
