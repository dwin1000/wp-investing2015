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

scriptLocation = "https://github.com/dwin1000/wp-investing2015/blob/master/shortInterest.py"

myList = ["SI/ZINC_SI", "SI/DTV_SI", "SI/CBI_SI"]

wpInfo = wpAuth.gmailAuth()
wpPasswd = wpInfo.passwd
wpLogin = wpInfo.login
wpServer = wpInfo.smtpServer
toAddr = wpInfo.recipents
fromSender = wpInfo.login+"@"+wpInfo.domain
subjectTitle = "Weekly Auto Short Interest Check"

def sendEmail(toWho, message, subject=subjectTitle,
    login=wpLogin, password=wpPasswd,
    fromAddr=fromSender, mailServer=wpServer):

    #header+='Cc: %s\n' % ','join(ccAddr)
    header='From:%s\n' % fromAddr
    header+='Subject: %s\n\n' % subject
    header+='To: \n'.join(toWho)

    message=header+message

    server = smtplib.SMTP(mailServer)

    """
    try:
        server.set_debuglevel(True)
        toVerify = server.verify(toAddr)
        ccVerify = server.verify(ccAddr)

        print "Address results: " , toVerify, ccVerify
    finally:
        server.quit()
    """

    server.starttls()
    server.login(login,password)
    output = server.sendmail(fromAddr,toWho,message)
    server.quit

def runQuandl(symbol):
    data = Quandl.get(symbol, authtoken="KhVeoKVw9GHh3qH6Wvt9",
        collapse='monthly',sort_order='desc',rows=5)
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

    sendEmail(toWho = toAddr, message = bodyMsg)


if __name__ == "__main__":
    main()
