#!/usr/bin/python

import mechanize
import cookielib
import re
from lxml import etree
import StringIO
import sys
import logging
import json
import itertools
import pandas as pd
import wpAuth

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
    %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class NestedDict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, NestedDict())

"""
def timer(fn, *args):
    import time
    start = time.clock()
    return fn(*args), time.clock() - start
"""

def header_path (id='Rf', loc=1, start=1, row=17):
    stripResult = []
    finalResult = []
    origPosition = []   # info to know how to get the real data
    tmpdict = {}

    xpathstring = ("//tr[@id='%s']/descendant-or-self::text()" % (id))
    result = tree.xpath(xpathstring)
    origSize = len(result)

    origttmHeading = result.index('TTM')
    logger.debug("Full raw Heading: %s %s" % (result, len(result)))

    for pos, element in enumerate(result):
        tmpdict.setdefault(element,[]).append(pos)
        stripdown = element.strip("\n").strip("\t").replace("\xa0","")
        if len(stripdown) != 0:
            stripResult.append(stripdown)
    ttmHeading = stripResult.index('TTM')
    fourBack = ttmHeading - 4

    finalResult.extend(stripResult[fourBack:ttmHeading+1])
    logger.debug("result to origttmHeading: %s" % result[:origttmHeading+1])

    # Need to add a "y-" to differentiate "yearly data". Anything to left of TTM
    # is yearly data
    #for mod in range(len(finalResult)):
    #    finalResult[mod] = "y-" + finalResult[mod]

    # Add back in "Fiscal Year" as the first element
    finalResult.insert(0,result[0])

    for entry in finalResult:
        origPosition.append(result[:origttmHeading+1].index(entry))

    logger.debug("1 finalResult: %s" % finalResult)
    logger.debug("1 origPosition: %s" % origPosition)

    finalResult.extend(stripResult[ttmHeading+1:])
    fttmHeading = finalResult.index('TTM')
    logger.debug("2 finalResult ttmHeading: %s" % finalResult[fttmHeading+1:])
    logger.debug("Total finalResult: %s" % finalResult)
    logger.debug("Result origttmHeading: %s " % result[origttmHeading+1:])

    for pos, entry in enumerate(finalResult[fttmHeading+1:]):
        if result.index(entry) in origPosition:
            origPosition.append(tmpdict[entry][1])
        else:
            origPosition.append(result.index(entry))

    logger.debug("2 origPosition: %s" % origPosition)

    zipped = dict(itertools.izip(origPosition, finalResult))
    logger.debug("zipped : %s" % zipped)

    return zipped


def x_pather(id='Rf',  loc=1, start=1, row=17, grp='val'):
    tmpArray = []
    tmpChange = []
    tmpHeader = []

    if id == 'Rf':
        xpathstring = ("//table[@id='%s']/tbody/tr[%d]/descendant-or-self::text()" % (id, loc))
        result = tree.xpath(xpathstring)

        logger.debug("Full raw result: %s - length - %s" % (result, len(result)))
        logger.error("rf Result: %s " % result)
        #sys.exit(1)

        for pos in sortedHeadings:
            if pos > len(result):
                item = "N0ne"
                logger.debug("rf set item to N0ne %s " % item )
            elif len(result[pos]) == 0:
                item = "N0ne"
            else:
                item = result[pos]

            logger.debug("rf result/stripped pos: %s " % item)
            aggResults[stock]["metrics"][result[0]][pos] = item

        # add in the type 'valuation|qualitative|ratio'
        aggResults[stock]["metrics"][result[0]]["type"] = grp


def main():
    global aggResults
    aggResults = NestedDict()
    aggList = {}

    #url = "https://www.gurufocus.com"
    gfStuff = wpAuth.gfInfo()
    url = gfStuff.Url
    gfUser = gfStuff.email
    gfPass = gfStuff.passwd

    stockList = ["MU"]
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    #br.set_all_readonly(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; \
        en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        # [('User-agent', 'Firefox')]

    br.open(url)
    br.follow_link(text_regex=r'LOG IN', nr=0)
    logger.info(br.title())
    br.select_form(nr=0)
    br.form["username"] = gfUser
    br.form["password"] = gfPass
    try:
        br.submit()
        logger.info(br.title())
    except Exception, e:
        sys.exit("failed: %d  %s " % (e.code, e.msg))

    for stock in stockList:
        global stock
        br.select_form(nr=0)
        br.form["keyword"] = stock
        try:
            br.submit()
            logger.info(br.title())
        except Exception, e:
            sys.exit("failed: %d  %s " % (e.code, e.msg))

        page = br.follow_link(text_regex=r'10-Y Financials', nr=0)
        logger.info(br.title())
        html = page.read()

        global tree
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO.StringIO(html), parser)

        wpHeader = { 'heading': {'field': 'header_scrol','location': 15},
        }

        wpMetrics = {'revPerShare': {'type': 'val', 'field': 'Rf', 'location': 4},
            'ebitdaPerShare': {'type': 'val', 'field':'Rf', 'location': 5},
            'cashflowPerShare': {'type': 'val', 'field': 'Rf', 'location': 9},
            'monthendStockPrice': {'type': 'val', 'field': 'Rf', 'location': 13},
            'ROE': {'type': 'qual', 'field': 'Rf', 'location': 17},
            'ROA': {'type': 'qual', 'field': 'Rf', 'location': 18},
            'ROIC': {'type': 'qual', 'field': 'Rf', 'location': 19},
            'rocGreen': {'type': 'qual', 'field': 'Rf', 'location': 20},
            'debtToEquity': {'type': 'qual', 'field': 'Rf', 'location': 21},
            'grossMargin': {'type': 'qual', 'field': 'Rf', 'location': 23},
            'opMargin': {'type': 'qual', 'field': 'Rf', 'location': 24},
            'netMargin': {'type': 'qual', 'field': 'Rf', 'location': 25},
            'revenue': {'type': 'qual', 'field': 'Rf', 'location': 43},
            'cogs': {'type': 'qual', 'field': 'Rf', 'location': 44},
            'cash': {'type': 'qual', 'field': 'Rf', 'location': 77},
            'goodwill': {'type': 'qual', 'field': 'Rf', 'location': 98},
            'ltDebt': {'type': 'qual', 'field': 'Rf', 'location': 111},
            'capEx': {'type': 'qual', 'field': 'Rf', 'location': 165},
            'fcf': {'type': 'qual', 'field': 'Rf', 'location': 166},
            'peRatio': {'type': 'ratio', 'field': 'Rf', 'location': 170},
            'priceFCF': {'type': 'ratio', 'field': 'Rf', 'location': 172},
            'psRatio': {'type': 'ratio', 'field': 'Rf', 'location': 173},
            'pegRatio': {'type': 'ratio', 'field': 'Rf', 'location': 174},
            'evToEBITDA': {'type': 'ratio', 'field': 'Rf', 'location': 176},
            'EYGreen': {'type': 'ratio', 'field': 'Rf', 'location': 178},
            'grahanNum': {'type': 'ratio', 'field': 'Rf', 'location': 192},
        }

        global outPos

        for title, cat in wpHeader.iteritems():
            logger.debug("%s %s \n" % (title, cat['field']))
            outZipped = header_path(id=cat['field'], \
                loc=cat['location'])

        for key, value in outZipped.iteritems():
            aggResults[stock]["headings"][key] = value

        global sortedHeadings
        sortedHeadings = sorted(aggResults[stock]["headings"].keys())

        logger.debug("sorted Headings keys: %s" % sortedHeadings)

        for title, cat in wpMetrics.iteritems():
            logger.debug("%s %s \n" % (title, cat['field']))
            x_pather(id=cat['field'], loc=cat['location'], grp=cat['type'])

        logger.debug("aggResults dict: %s", aggResults)
        logger.debug("aggResults keys: %s", aggResults.keys())

        # write json object out to disk to play around with later
        jsonDump = json.dumps(aggResults, indent=3, default=str, ensure_ascii=True)
        logger.debug("type of jsondump: %s" % type(jsonDump))
        tmpFile = "gfRepo/" + stock + ".json"
        with open(tmpFile, "w+") as diskfile:
            json.dump(jsonDump, diskfile, indent=2, skipkeys=True, ensure_ascii=False)

        logger.debug("all the metrics: %s" % type(aggResults[stock]["metrics"]))
        newDict = aggResults[stock]["metrics"]
        logger.debug("newDict type: %s" % type(newDict))
        logger.debug("newDict: %s" % newDict)
        #pDataF = pd.DataFrame(data = newDict, columns=headers)
        #  sorted Headings keys: [0, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32]
        pd.set_option('display.max_columns', 400)
        pd.set_option('display.width', 130)
        pDataF = pd.DataFrame(newDict)
        transF = pDataF.T   #inverse x,y axis
        transFindex = transF.columns
        for i in transFindex:       # renaming the numeric index to date "Sep14, Mar14, etc"
            if i != 'type':
                transF.rename(columns = {i:aggResults[stock]["headings"][i]}, inplace=True )

        logger.debug("panda df: %s" % transF) # swap index with columns
        transF.drop('Fiscal Period', axis=1, inplace=True)
        transF = transF.groupby(['type'])
        #transF = transF.drop(['Fiscal Policy'])

        for g, h in transF:
            print h
            print "\n"

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error("Exception caught: %s" % e)
        sys.exit(1)
