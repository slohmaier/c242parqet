import pandas as pd
import os
import sys
import csv
import re
from argparse import ArgumentParser

REGEX_HOLDING_URL = re.compile(r'https://app\.parqet\.com/p/\w+/h/(?P<holdingid>\w+)')

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-c', '--csv', help='CSV file to load', required=True)
    argparser.add_argument('-p', '--parqetcsv', help='Output parqet csv', required=True)
    argparser.add_argument('--hurl', '-u', dest='hurl', required=True,
        help='Link to the Holding in Parqet https://app.parqet.com/p/[PORTFOLIOID]/h/[HOLDING-ID]')
    # argument for tax percent with default 27.9951
    argparser.add_argument('-t', '--tax', help='Tax percent', default=27.9951)
    # add argument to transfer out interests
    argparser.add_argument('-i', '--interest', help='Transfer out interests', action='store_true')
    
    args = argparser.parse_args()

    transferOut = args.interest
    #check if arguments are valid
    csv_file = args.csv
    if os.path.isfile(csv_file) == False:
        print("CSV file does not exist")
        sys.exit()
    parqet_csv_file = args.parqetcsv
    match = REGEX_HOLDING_URL.match(args.hurl)
    if match is None:
        sys.stderr.write('Holding Url "{0}" does not match the pattern! Try {1} -h.\n'
            .format(args.hurl, sys.argv[0]))
        sys.exit(1)
    holdingId = match.group('holdingid')
    taxPercent = float(args.tax)

    df = pd.read_csv(csv_file)

    # These are the columngs:
    # ['Transaktionstyp',
    #  'Buchungsdatum',
    #  'Betrag',
    #  'Zahlungsempfänger',
    #  'IBAN',
    #  'BIC',
    #  'Verwendungszweck',
    #  'Beschreibung',
    #  'Kategorie',
    #  'Unterkategorie']

    rows = []
    for index, row in df.iterrows():
        date = row['Buchungsdatum']
        amount = row['Betrag']
        amount = float(amount.replace('"', '').replace(',', '.'))
        tax = 0.0

        if row['Transaktionstyp'] == 'Zinszahlung':
            transtype = 'Interest'
            tax = amount * taxPercent / 100
        elif row['Transaktionstyp'] != 'Abbuchung':
            transtype = 'TransferIn'
            if amount < 0:
                transtype = 'TransferOut'
                amount = -amount
        else:
            continue

        amount = '%.4f' % amount
        tax = '%.4f' % tax
        rows.append([date, amount, tax, '0', transtype, holdingId])

    if rows == []:
        sys.exit()

    pcsvFile = open(parqet_csv_file, 'w+')
    pcsv = csv.writer(pcsvFile, 'unix', quoting=0, delimiter=';')
    pcsv.writerow(['date', 'amount', 'tax', 'fee', 'type', 'holding'])
    for row in rows:
        pcsv.writerow(row)
