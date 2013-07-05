'''
Created on Jul 3, 2013

@author: sdejonckheere
'''
import csv
from underlyings.models import Currency, Country, Type, FinancialAsset, SubType,\
    Track, TrackToken
from underlyings import models
from _pyio import __metaclass__
from abc import ABCMeta
from django.template.base import kwarg_re
import abc

# http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works
class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next() 
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num

class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)

def populate_from_datasources():
    # Currencies
    Currency.objects.all().delete()
    currencies_file = open('C:\\DEV\\Workspaces\\Python\\seq_data_manager\\datasources\\currencies-header.csv')
    for currency in UnicodeDictReader(currencies_file):
        new_currency = Currency()
        new_currency.name =  currency[u'name']
        new_currency.short_name =  currency[u'code']
        new_currency.iso_code_2 = currency[u'country']
        new_currency.iso_code_3 = currency[u'code']
        new_currency.iso_symbol = currency[u'symbol']
        new_currency.save()
    currencies_file.close()
    
    # Countries
    Country.objects.all().delete()
    countries_file = open('C:\\DEV\\Workspaces\\Python\\seq_data_manager\\datasources\\countries-header.csv')
    for country in UnicodeDictReader(countries_file):
        new_country = Country()
        new_country.name =  country[u'name']
        new_country.short_name =  country[u'code3']
        new_country.iso_code_2 = country[u'code']
        new_country.iso_code_3 = country[u'code3']
        new_country.currency_iso_code_3 = country[u'currency']
        new_country.save()
    countries_file.close()
    
    # Link countries to currencies
    currencies = Currency.objects.all()
    for currency in currencies:
        countries = Country.objects.filter(currency_iso_code_3=currency.iso_code_3)
        for country in countries:
            currency.countries.add(country)
        currency.save()
    
    # Types
    Type.objects.all().delete()
    types_file = open('C:\\DEV\\Workspaces\\Python\\seq_data_manager\\datasources\\types-header.csv')
    for type_ in UnicodeDictReader(types_file):
        new_type = Type()
        for key in type_.keys():
            setattr(new_type,key,type_[key])
        new_type.save()
    types_file.close()

    # Target wrk_models
    wrk_models = [FinancialAsset,Track]
    for model in wrk_models:
        model_file = open('C:\\DEV\\Workspaces\\Python\\seq_data_manager\\datasources\\' + str(model.__name__).lower() + '-header.csv')
        for entry in UnicodeDictReader(model_file):
            new_model = model()
            for key in entry.keys():
                if key=='target':
                    continue
                elif str(key).endswith('target_type'):
                    target_class = getattr(models, entry['target_type'])
                    targets = target_class.objects.filter(name=entry['target'])
                    if len(targets)>0:
                        setattr(new_model,'target',targets[0])
                elif str(key).endswith('sub_type'):
                    m_types = SubType.objects.filter(target=str(model.__name__),name=entry[key])
                    if len(m_types)>0:
                        setattr(new_model,key,m_types[0])
                elif str(key).endswith('type'):
                    m_types = Type.objects.filter(target=str(model.__name__),name=entry[key])
                    if len(m_types)>0:
                        setattr(new_model,key,m_types[0])
                else:
                    if len(entry[key]):
                        setattr(new_model,key,entry[key])
            new_model.save()
        model_file.close()
        
class TrackUpdater():
    __metaclass__ = ABCMeta
    
    @abc.abstractmethod
    def get_data_as_list(self,source,**kwarg):
        """
            Place here your code
        """
        return []
    
    def import_data_from_list(self, data, allow_update):
        tokens = []
        for row in data:
            token = getattr(models,row['type'])() # TODO: Try catch me
            for key in row.keys():
                if key!='type' and key!='track':
                    setattr(token, key, row[key])
                elif key=='track':
                    None
            tokens.append(token)
        