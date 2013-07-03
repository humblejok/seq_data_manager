'''
Created on Jul 3, 2013

@author: sdejonckheere
'''
import csv

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell.encode('utf-8'), 'utf-8') for cell in row]

def populate_from_datasources():
    # Currencies
    currencies_file = open('C:\\DEV\\Workspaces\\Python\\seq_data_manager\\datasources\\currencies.csv')
    
    currencies = unicode_csv_reader(currencies_file,delimiter=',')
    for currency in currencies:
        print ' - '.join(currency)   
    
    currencies_file.close()