#!/usr/bin/env python

#
# Syra Systems Transaction Data Scraper
#
# http://github.com/macropin/Syra2CSV
#


from datetime import datetime
from decimal import Decimal

import os
import csv
import cookielib, urllib, urllib2
from BeautifulSoup import BeautifulSoup

from settings import *

# Help from http://kentsjohnson.com/kk/00010.html
# http://docs.python.org/library/urllib2.html#examples
# Beautiful Soup Documentation http://www.crummy.com/software/BeautifulSoup/documentation.html

# Constants
LOGIN_URL = 'https://www.secureapi.com.au/reseller/home/reseller_login/'
DOWNLOAD_URL = 'https://www.secureapi.com.au/reseller/reseller/reseller_view_payments/'
LOGIN_FORM=dict(submitted='TRUE', reseller_username=RESELLER_USERNAME, reseller_password=RESELLER_PASSWORD, submit='Login Now')


def login(LOGIN_FORM, LOGIN_URL):

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)

    params = urllib.urlencode(LOGIN_FORM)

    # login submit
    f = opener.open(LOGIN_URL, params)
    page = f.read()
    f.close()

    return opener


def parse_report_page(page):

    # Parse the index page 'report'
    soup = BeautifulSoup(page)
    data = soup.findAll('tr', attrs = {'class':'productsRow'})

    data_obj = []

    saasu_obj = []

    for tr in data:
        row = tr.findAll('td')
        row_obj = {
            'invoice': row[0].find('a').contents[0],
            'date': datetime.strptime(row[1].contents[0], '%d %b %Y'),
            'paid': Decimal(row[2].find('div').contents[0].strip('$ ')),  # transaction amount
            'profit': Decimal(row[3].find('div').contents[0].strip('$ ')),
            'currency': row[4].contents[0],
            'paid_by': row[5].contents[0],
            }

        # Saasu CSV	Format: Date, Amount, Description, Reference
        # As per discussions with accountant, treat positive transactions as 'fee received' (income / sale)
        # negative transactions are purchases against reseller credit (cost of sales)

        if row_obj['profit'] > 0:
            saasu_row_obj = (
                            row_obj['date'],
                            Decimal(row_obj['profit']),
                            'Domain Sale Commission. Transaction total %s. Syra Invoice %s.' % (row_obj['paid'], row_obj['invoice']),
                            'Paid by %s' % (row_obj['paid_by']),
                            )
        else:
            saasu_row_obj = (
                row_obj['date'],
                Decimal(row_obj['profit']),
                'Cost of Sales. Transaction total %s. Syra Invoice %s.' % (row_obj['paid'], row_obj['invoice']),
                'Paid by %s' % (row_obj['paid_by']),
                )

        saasu_obj.append(saasu_row_obj)
        data_obj.append(row_obj)

        # Download detail page
        # TODO: Download / parse the detail and use it for the description.
        #download_detail_page(opener, row_obj['invoice'], TEMP_DIR)

    return saasu_obj, data_obj


# TODO: NB, this function is not actually used.
def download_detail_page(opener, invoice, TEMP_DIR):

    fname = '%s.html' % (invoice,)
    fpath = os.path.join(TEMP_DIR, fname)

    # get the next page
    DOWNLOAD_URL = '%s%s' % ('http://www.secureapi.com.au/reseller/reseller/reseller_view_invoice/?invoice=', invoice)
    f = opener.open(DOWNLOAD_URL)
    page = f.read()
    f.close()

    # write file out to disk
    f = open(fpath, 'w')
    f.write(page)
    f.close()

    return page

#
#def parse_detail_page(data_obj):
#
#    # Parse the detail page
#    for row in data_obj:
#        invoice = row['invoice']
#
#
#        # Download the detail page
#        if DO_DOWNLOAD:
#
#            download_detail_page(opener, invoice, TEMP_DIR)
#
#        else:
#            f = open(fpath, 'r')
#            page = f.read()
#            f.close()
#
#        # Parse the detail page
#        soup = BeautifulSoup(page)
#        for table in soup.findAll('table', attrs = {'width':'560'} ): #.findNext('tr'):
#            if DEBUG:
#                print table
#
#                #print data
#                #data = soup.find(text='Product Details').findNext('tr')
#                #print soup.find(text='Product Details')
#
#                print '*****************************************'
#
#    return None # We haven't actually done any useful work yet.


def append_saasu_csv(saasu_obj):

    # Saasu CSV	Format: Date, Amount, Description, Reference
    # http://help.saasu.com/import/

    fpath = os.path.join(TEMP_DIR, 'report.csv')

    file = open(fpath, 'a')
    writer = csv.writer(file, dialect='excel')

    for row in saasu_obj:
        writer.writerow(row)

    file.close()


#
# Main Loop
#

for i in range(1,REPORT_PAGES_SCRAPE+1):

    fname = '%s_%s.html' % ('report', i)
    fpath = os.path.join(TEMP_DIR, fname)

    if DO_DOWNLOAD:
        # Download the index page 'report'

        opener = login(LOGIN_FORM, LOGIN_URL)

        # get the page
        f = opener.open('%s?page=%s' % (DOWNLOAD_URL, i))
        page = f.read()
        f.close()

        # write file out to disk
        f = open(fpath, 'w')
        f.write(page)
        f.close()

    else:
        # Or get the page from disk (manually downloaded)
        f = open(fpath, "r")
        page = f.read()
        f.close()

    # Parse the page
    saasu_obj, data_obj = parse_report_page(page)
    append_saasu_csv(saasu_obj)
