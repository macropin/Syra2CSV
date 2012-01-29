from datetime import datetime
from decimal import Decimal

import os
import csv
import cookielib, urllib, urllib2
from BeautifulSoup import BeautifulSoup

from settings import *

# Help from http://kentsjohnson.com/kk/00010.html
# http://docs.python.org/library/urllib2.html#examples

LOGIN_URL = 'https://www.secureapi.com.au/reseller/home/reseller_login/'
DOWNLOAD_URL = 'https://www.secureapi.com.au/reseller/reseller/reseller_view_payments/'
LOGIN_FORM=dict(submitted='TRUE', reseller_username=RESELLER_USERNAME, reseller_password=RESELLER_PASSWORD, submit='Login Now')

# Download the index page 'report'
if DO_DOWNLOAD:

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)

    params = urllib.urlencode(LOGIN_FORM)

    # login submit
    f = opener.open(LOGIN_URL, params)
    page = f.read()
    f.close()

    # get the page
    f = opener.open(DOWNLOAD_URL)
    page = f.read()
    f.close()

else:

    # Or get the page from disk (manually downloaded)
    f = open('./report.html', "r")
    page = f.read()
    f.close()

# Parse the index page 'report'
# (Documentation http://www.crummy.com/software/BeautifulSoup/documentation.html)
soup = BeautifulSoup(page)
data = soup.findAll('tr', attrs = {'class':'productsRow'})

data_obj = []

saasu_obj = []

for tr in data:
    row = tr.findAll('td')
    row_obj = {
        'invoice': row[0].find('a').contents[0],
        'date': datetime.strptime(row[1].contents[0], '%d %b %Y'),
        'paid': Decimal(row[2].find('div').contents[0].strip('$ ')),
        'profit': Decimal(row[3].find('div').contents[0].strip('$ ')),
        'currency': row[4].contents[0],
        'paid_by': row[5].contents[0],
        }

    saasu_row_obj = (
                    datetime.strptime(row[1].contents[0], '%d %b %Y'),
                    Decimal(row[2].find('div').contents[0].strip('$ ')),
                    Decimal(row[3].find('div').contents[0].strip('$ ')),
                    row[5].contents[0],
                    )

    saasu_obj.append(saasu_row_obj)
    data_obj.append(row_obj)


#for row in data_obj:
#
#    #xx = row['date']
#    #xx = u'16 Nov 2011'
#
#    #print datetime.strptime(xx, '%d %b %Y' ) # 21 Jul 2010
#
#    for key in row.items():
#        print "%s," % (key[1],)



# Parse the detail page
for row in data_obj:
    invoice = row['invoice']
    fname = '%s.html' % (invoice,)
    fpath = os.path.join(TEMP_DIR, fname)

    # Download the detail page
    if DO_DOWNLOAD:

        # get the next page
        DOWNLOAD_URL = '%s%s' % ('http://www.secureapi.com.au/reseller/reseller/reseller_view_invoice/?invoice=', invoice)
        f = opener.open(DOWNLOAD_URL)
        page = f.read()
        f.close()

        # write file out to disk

        f = open(fpath, 'w')
        f.write(page)
        f.close()

    else:
        f = open(fpath, 'r')
        page = f.read()
        f.close()

    # Parse the detail page
    soup = BeautifulSoup(page)
    for table in soup.findAll('table', attrs = {'width':'560'} ): #.findNext('tr'):
        if DEBUG:
            print table
    
            #print data
            #data = soup.find(text='Product Details').findNext('tr')
            #print soup.find(text='Product Details')

            print '*****************************************'


# Saasu CSV	Format: Date, Amount, Description, Reference
# http://help.saasu.com/import/

fpath = os.path.join(TEMP_DIR, 'report.csv')

file = open(fpath, 'w')
writer = csv.writer(file, dialect='excel')

for row in saasu_obj:
    writer.writerow(row)

file.close()

