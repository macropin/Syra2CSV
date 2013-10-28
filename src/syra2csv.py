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
LOGIN_FORM = dict(submitted='TRUE', reseller_username=RESELLER_USERNAME, reseller_password=RESELLER_PASSWORD, submit='Login Now')


def login(LOGIN_FORM, LOGIN_URL):
    """
        Login to Syra, return a urllib obj
    """

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    urllib2.install_opener(opener)

    params = urllib.urlencode(LOGIN_FORM)

    # login submit
    f = opener.open(LOGIN_URL, params)
    page = f.read()
    f.close()

    return opener


def parse_report_page(page):
    """
        Parse the financial transaction report page and return two dicts, generic and saasu
    """

    # Parse the index page 'report'
    soup = BeautifulSoup(page)
    data = soup.findAll('tr', attrs = {'class':'productsRow'})

    data_obj = []

    saasu_obj = []

    for tr in data:

        row = tr.findAll('td')

        invoice = row[0].find('a').contents[0]

        # Download detail page
        if DO_DOWNLOAD:
            download_detail_page(opener, invoice, TEMP_DIR)
        # Parse Details
        client_amount, details = parse_invoice_detail_page(invoice, TEMP_DIR)

        row_obj = {
            'invoice': invoice,
            'date': datetime.strptime(row[1].contents[0], '%d %b %Y'),
            'paid': Decimal(row[2].contents[0].strip('$')),  # transaction amount
            'profit': Decimal(row[3].contents[0].strip('$ ')),
            'client_amount': client_amount, # amount paid by client, includes credit card fees (if paid by CC)
            'currency': row[4].contents[0],
            'paid_by': row[5].contents[0],
            'details': details, # transation details, eg domains sold
            }

        # Saasu CSV	Format: Date, Amount, Description, Reference

        # Important Details About the Logic:
        # As per discussions with accountant, we treat:
        # Positive transactions as 'fee received' (income / sale) (easy!)
        # Negative and Zero profit transactions are COGS (cost of sales) or Expense transactions (depending on whether we resold them, or for internal use)
        # In the case of COGS we have manually invoiced the client in Saasu. (invoiced outside of Syra)
        # For these COGS / Expense transactions, if they are paid by Credit Card, then we manually update the payment method in Saasu after importing to reflect the payment from our own corp CC.

        if row_obj['profit'] > 0:
            saasu_row_obj = (
                row_obj['date'],
                Decimal(row_obj['profit']),
                'Commission Income. Transaction total %s. Syra Invoice %s. Details: %s.' % (row_obj['paid'], row_obj['invoice'], row_obj['details']),
                'Paid by %s' % (row_obj['paid_by']),
                )
        else:
            saasu_row_obj = (
                row_obj['date'],
                Decimal(-row_obj['client_amount']),
                'COGS or Expense. Transaction total %s. Syra Invoice %s. Details: %s.' % (row_obj['paid'], row_obj['invoice'], row_obj['details']),
                'Paid by %s' % (row_obj['paid_by']),
                )

        saasu_obj.append(saasu_row_obj)
        data_obj.append(row_obj)

    return saasu_obj, data_obj


def download_detail_page(opener, invoice, TEMP_DIR):
    """
        Download the transaction detail pages and save to disk
    """
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


def parse_invoice_detail_page(invoice, TEMP_DIR):
    """
        Parse the Invoice Detail page, previously downloaded
        Returns, the client transaction amount and a summary of the transaction detail
    """
    fname = '%s.html' % (invoice,)
    fpath = os.path.join(TEMP_DIR, fname)

    # open already downloaded file
    f = open(fpath, 'r')
    page = f.read()
    f.close()

    # Parse the detail page
    soup = BeautifulSoup(page)

    # Get client charged amount
    client_amount = Decimal(soup.find(text='Client Total Invoice:').findParent('tr').findAll('td')[1].contents[0].strip('$').strip(' AUD'))
    if DEBUG:
        print client_amount

    # Get sale details
    details = ''
    for details_td in [a.findParents('table')[0].findAll('td')[2:] for a in (td.find(text='Product') for td in soup.findAll("td", {"class": "productDesc"})) if a]:
        details = details + details_td[0].renderContents() + ' ' + details_td[1].renderContents()
    if DEBUG:
        print details

    return client_amount, details


def append_saasu_csv(saasu_obj):
    """
        Append our saasu dict to our output csv
    """

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
