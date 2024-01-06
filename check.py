import pandas as pd
import os 


#print all files starting with _
print([f for f in os.listdir() if f.startswith('_')])

#read all csv's starting with '_', parse them with pandas and merge all data
#into one dataframe
df = pd.concat([pd.read_csv(f, delimiter=';') for f in os.listdir() if f.startswith('_')])

#print all columns
print(df.columns)

#make amount column and tax columng floting point numbers
df['amount'] = df['amount'].astype(float)
df['tax'] = df['tax'].astype(float)

#get all amounts indicidually for TransferIn and TransferOut
total_transfer_in = df[df['type'] == 'TransferIn']['amount'].sum()
total_transfer_out = df[df['type'] == 'TransferOut']['amount'].sum()

#sum up all taxes
total_tax = df['tax'].sum()

#output transfer in, transfer out, totala_amount=transfer_in-transfer_out, total_tax with nice description
print('TransferIn: {0:.2f}'.format(total_transfer_in))
print('TransferOut: {0:.2f}'.format(total_transfer_out))
print('TotalAmount: {0:.2f}'.format(total_transfer_in - total_transfer_out))
print('TotalTax: {0:.2f}'.format(total_tax))
