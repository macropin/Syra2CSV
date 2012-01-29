# Aust Domains (Syra Systems) Reseller Transactions to CSV

Problem: Aust Domains / Syra Systems do not provide an API for extracting the financial transaction information from their reseller system.

Solution: This little hacky script screen-scrapes the reseller website and converts the financial transactions into a CSV file which
can be imported into your favourite accounting package. We use Saasu, so the CSV format is the Saasu CSV format.

## Getting started

1. Make sure you have the required python deps installed (eg Beautiful Soup). See ./deployment/pip-reqs.txt for pip requirements

2. Set your username and password in ./src/settings.py

3. Run ./src/syra2csv.py. If all goes well your csv extract should be found in ./tmp/report.csv

- Andrew Cutler
