#!/usr/bin/python
"""
Author: Darren Nguyen
Date: 3/25/2015

Script to download short interest on a list of stocks.
The results will be emailed out using the smtplib.
The auth info is extracted from the wpAuth module

Reference: check www.quandl.com
"""

import Quandl
import smtplib
import StringIO
import wpAuth
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import os
import sys

scriptLocation = "https://github.com/dwin1000/wp-investing2015/blob/master/shortInterest.py"

myList = ["SI/ZINC_SI", "SI/DTV_SI", "SI/CBI_SI"]

wpInfo = wpAuth.gmailAuth()
wpPasswd = wpInfo.passwd
wpLogin = wpInfo.login
wpServer = wpInfo.smtpServer
fromSender = wpInfo.login+"@"+wpInfo.domain

# Protection mode for either testing, running through cron
if len(sys.argv) > 1:
    # if we will run through cron and even if "test" exists
    toAddr = wpInfo.recipents
else:
    # if cmd line && file exists, send to test
    if os.path.isfile('test'):
        toAddr = wpInfo.testrecipents
    # if someone else runs from cmdline && not in test mode
    else:
        toAddr = wpInfo.recipents

tokenQuandl = wpAuth.quandlInfo()
token = tokenQuandl.authtoken

subjectTitle = "Weekly Auto Short Interest Check"

def sendEmail(message, toWho=toAddr, subject=subjectTitle,
    login=wpLogin, password=wpPasswd,
    fromAddr=fromSender, mailServer=wpServer):

    header=MIMEMultipart()
    header['From'] = fromAddr
    header['To'] = ", ".join(toWho)
    header['Subject'] = subject
    #header+='Cc: %s\n' % ','join(ccAddr)
    #header='From:%s\n' % fromAddr
    #header+='To: %s \n' % ",".join(toWho)
    #header+='Subject: %s \n\n' % subject

    header.attach(MIMEText(message,'plain'))
    mailMsg = header.as_string()
    print mailMsg

    mailConn = smtplib.SMTP(mailServer)

    """
    try:
        server.set_debuglevel(True)
        toVerify = server.verify(toAddr)
        ccVerify = server.verify(ccAddr)

        print "Address results: " , toVerify, ccVerify
    finally:
        server.quit()
    """

    mailConn.starttls()
    mailConn.login(login,password)
    output = mailConn.sendmail(fromAddr,toWho,mailMsg)
    mailConn.quit

def runQuandl(symbol):
    # calling quandl api, inputting specific dataset
    #data = Quandl.get(symbol, authtoken="KhVeoKVw9GHh3qH6Wvt9",
    data = Quandl.get(symbol, authtoken=token,
        collapse='weekly',sort_order='desc',rows=5)
    return data

def main():
    # write to memory since numpy output can't be converted to string
    outString = StringIO.StringIO()

    for x in myList:
        output = runQuandl(x)
        outString.write("\n"+x+"\n")
        print >> outString, output

    outString.write("\n\nScript Location: %s" % scriptLocation)
    bodyMsg = outString.getvalue()

    sendEmail(toWho=toAddr, message=bodyMsg)
    outString.close()

if __name__ == "__main__":
    main()
