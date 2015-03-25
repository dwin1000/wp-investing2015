#!/usr/bin/python
"""
authtoken='KhVeoKVw9GHh3qH6Wvt9'
Sample objects and methods from Quandl
https://www.quandl.com/api/v1/datasets/WIKI/AAPL.csv?
sort_order=asc
exclude_headers=true
rows=3
trim_start=2012-11-01
trim_end=2013-11-30
column=4
collapse=quarterly
transformation=rdiff

Reference: check www.quandl.com
"""

import Quandl
import smtplib
import StringIO

toAddr = ["dwin1000@gmail.com","wliu73@gmail.com"]
subjectTitle = "Weekly Auto Short Interest Check"

def sendEmail(toWho, subject, message,
    login='wpmailsend', password='2island$life',
    fromAddr='wpmailsend@gmail.com', mailServer='smtp.gmail.com:587'):

    #header+='Cc: %s\n' % ','join(ccAddr)
    header='From:%s\n' % fromAddr
    header+='To: \n'.join(toWho)
    header+='Subject: %s\n\n' % subject

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


def main():
    # write to memory since numpy output can't be converted to string
    outString = StringIO.StringIO()

    dataZINC = Quandl.get("SI/ZINC_SI", authtoken="KhVeoKVw9GHh3qH6Wvt9",
        collapse='monthly',sort_order='desc',rows=5)
    dataCBI = Quandl.get("SI/CBI_SI", authtoken="KhVeoKVw9GHh3qH6Wvt9",
        collapse='monthly',sort_order='desc',rows=5)
    dataDTV = Quandl.get("SI/DTV_SI", authtoken="KhVeoKVw9GHh3qH6Wvt9",
        collapse='monthly',sort_order='desc',rows=5)
    """
    bodyMsg = 'ZINC: \n'
    bodyMsg += dataZINC
    bodyMsg += 'DTV: \n'
    bodyMsg += dataDTV
    bodyMsg += 'CBI: \n'
    bodyMsg += dataCBI
    """
    outString.write("\nZINC \n")
    print >> outString, dataZINC
    outString.write("\nDTV \n")
    print >> outString, dataDTV
    outString.write("\nCBI \n")
    print >> outString, dataCBI

    bodyMsg = outString.getvalue()

    sendEmail(subject = subjectTitle, toWho = toAddr, message = bodyMsg)
if __name__ == "__main__":
    main()
