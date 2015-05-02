#!/usr/bin/python

import wpAuth
import gfLogin
import csv
import sys
import pandas as pd
import numpy as np
import logging
import logging.config

debugLevel = "DEBUG"
global logger
logger = logging.getLogger(__name__)
logger.setLevel(debugLevel)

ch = logging.StreamHandler()
ch.setLevel(debugLevel)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
        %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class my_dialect(csv.Dialect):
    lineterminator = '\n'
    delimiter = '\t'
    quotechar = '"'
    quoting = 1

def writeOut(df, csvFile):
    df.to_csv(csvFile, sep='\t')

def pd_workIt(guru, id, xlsfile, finalDF):

    with open(xlsfile, "rb") as f:
        reader = list(csv.reader(f, dialect=my_dialect))
        header, values = reader[4], reader[5:]

    df = pd.DataFrame(values, columns=header)
    df["guru"] = guru       # Add in the name of the guru
    df["Number of Shares"] = df["Number of Shares"].convert_objects(convert_numeric=True)
    df["Value ($1000)"] = df["Value ($1000)"].convert_objects(convert_numeric=True)
    df["% of Company"] = df["% of Company"].convert_objects(convert_numeric=True)

    logger.debug("df.types: %s" % df.dtypes)

    #filterEd = df.sort(["Number of Shares"], ascending=False).head(2)
    filterEd = df.sort(["Value ($1000)"], ascending=False).head(3)
    finalDF = finalDF.append(filterEd)

    return finalDF

def main():
    xlsdir = "gfTopHoldings/"
    headers = ["Symbol", "Company", "Price ($)", "Sector", "Industry", "Category",
               "Sub-Category", "Region", "Market Cap ($M)", "Number of Shares",
               "Value ($1000)", "Percentage (%)", "Change from the previous Quarter (%)",
               "As of Date", "% of Company", "Trade Impact To Portfolio (%)" ]

    # Initialize empty pd frame
    finalDf = pd.DataFrame(data=np.zeros((0,len(headers))), columns=headers)

    guruDict = {
                "Buffet": "7",
                "Whitman": "12",
                "Einhorn": "39",
                "Pabrai": "51",
                "Soros": "65",
                "Berkowitz": "22",
                "Klarman": "28",
                "Tepper": "65",
                "Icahn": "67",
                "Ackman": "47",
                "Watsa": "78",
                "Paulson": "85",
                "Yachtman": "91",
                "Abrams": "104",
                "Chou": "133",
                "Dalio": "147",
                "Ubben": "184",
                 }


    user, passwd, url = gfLogin.setUp_WPauth()

    """
    try:
        br = gfLogin.login_gf(url, user, passwd)
    except Exception, e:
        logger.error("Can't login to GF: %s" % e)
        sys.exit(1)
    """

    for guru, id in guruDict.iteritems():
        link = "http://www.gurufocus.com/download_holdings.php?guru_id=" + id + "&portname=0"
        xlsfile = xlsdir + guru + ".xls"

        logger.debug("link: %s  xlsfile: %s" % (link, xlsfile))

        try:
            ##br.retrieve(link, xlsfile)
            finalDf = pd_workIt(guru, id, xlsfile, finalDf)
        except Exception, e:
            logger.error("Can't retrieve xls file for %s: %s" % (guru,e))

    finalDf = finalDf.sort(["Value ($1000)"], ascending=False)
    filterDf = finalDf[['Symbol', 'guru', 'Number of Shares', 'Value ($1000)',
                '% of Company', 'Change from the previous Quarter (%)',
                'Percentage (%)', 'As of Date', 'Price ($)']]
    logger.debug("finalDf: %s" % finalDf )
    type(finalDf)

    csvFile = xlsdir + "GurusTopHoldings.xls"
    writeOut(filterDf, csvFile)

    return finalDf, filterDf

if __name__ == "__main__":
    main()
    # For debugging through ipython
    #(new, tmpDf) = main()