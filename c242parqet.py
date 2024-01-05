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
    # argument for modes: 'all', 'transactions', 'interest'
    argparser.add_argument('-m', '--mode', help='Mode: all, transactions, interest', required=True)
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
    mode = args.mode
    if mode not in ['all', 'transactions', 'interest']:
        print("Mode must be one of 'all', 'transactions', 'interest'")
        sys.exit()
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
    if mode == 'all':
        raise NotImplementedError("Not implemented yet")
    elif mode == 'transactions':
        Transaktionstypen = ['Pocket-Umbuchung', 'Sparen', 'SEPA-Überweisung', 'SEPA-Gutschrift']
        df = df[df['Transaktionstyp'].isin(Transaktionstypen)]
        for index, row in df.iterrows():
            date = row['Buchungsdatum']
            amount = row['Betrag']
            amount = float(amount.replace('"', '').replace(',', '.'))

            transtype = 'TransferIn'
            if amount < 0:
                transtype = 'TransferOut'
                amount = -amount
            #make amount .2 string
            amount = '{:.2f}'.format(amount)
            rows.append([date, amount, '0', '0', transtype, holdingId])
    elif mode == 'interest':
        #search for row with columngs 'Abbuchung' and 'Zinszahlung'
        df = df[df['Transaktionstyp'].isin(['Abbuchung', 'Zinszahlung'])]
        taxDf = df[df['Transaktionstyp'] == 'Abbuchung']
        #forech row in 'Zinszahlung' search for row with 'Abbucuhung' and same date
        for index, row in df.iterrows():
            if row['Transaktionstyp'] == 'Zinszahlung':
                date = row['Buchungsdatum']
                amount = row['Betrag']
                amount = float(amount.replace('"', '').replace(',', '.'))
                tax = amount * taxPercent / 100
                amountOut = amount - tax
                #get Intereset
                amount = '{:.2f}'.format(amount)
                tax = '{:.2f}'.format(tax)
                amountOut = '{:.2f}'.format(amountOut)
                rows.append([date, amount, tax, '0', 'Interest', holdingId])
                if transferOut:
                    rows.append([date, amountOut, '0', '0', 'TransferOut', holdingId])

    if rows == []:
        sys.exit()

    pcsvFile = open(parqet_csv_file, 'w+')
    pcsv = csv.writer(pcsvFile, 'unix', quoting=0, delimiter=';')
    pcsv.writerow(['date', 'amount', 'tax', 'fee', 'type', 'holding'])
    for row in rows:
        pcsv.writerow(row)  