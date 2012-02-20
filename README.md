# Syra Systems (Aust Domains / Crazy Domains) Reseller Transactions to CSV

Problem: Aust Domains / Syra Systems do not provide an API for extracting the financial transaction information from their reseller system.

Solution: This little hacky script screen-scrapes the reseller website and converts the financial transactions into a CSV file which
can be imported into your favourite accounting package. We use Saasu, so the CSV format is the Saasu CSV format.

## Getting started

1. Make sure you have the required python deps installed (eg Beautiful Soup). See ./deployment/pip-req.txt for pip requirements

2. Set your username and password in ./src/settings.py

3. Run ./src/syra2csv.py. If all goes well your csv extract should be found in ./tmp/report.csv

## Importing into Saasu

1. Create the appropriate COGS and Income accounts for domain sales / purchases.

2. Create a 'bank account' for Syra Systems transactions to be imported into.

3. Then using the Saasu import transaction feature, import the CSV file into the 'bank' account created previously.

4. Finally create either 'COGS Purchases' or 'Commission Sales' items for the transactions imported.

NB. COGS purchases are those where the items where paid for by reseller credit and are a negative transaction,
whereas the positive transactions paid for by credit card are treated as commission sales.

-- Andrew Cutler
