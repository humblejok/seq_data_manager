from django.db import models
import datetime

class NamedObject(models.Model):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=128, null=True, blank=True)
    
class IdentifiableObject(NamedObject):
    id_internal_code = models.CharField(max_length=128, null=True, blank=True)
    id_ticker = models.CharField(max_length=64, null=True, blank=True)
    id_bloomberg_id = models.CharField(max_length=64, null=True, blank=True)
    id_bloomberg_full_ticker = models.CharField(max_length=128, null=True, blank=True)
    id_cusip = models.CharField(max_length=64, null=True, blank=True)
    id_isin = models.CharField(max_length=64, null=True, blank=True)
    id_sedol = models.CharField(max_length=64, null=True, blank=True)
    id_ric_code = models.CharField(max_length=64, null=True, blank=True)
    id_wkn = models.CharField(max_length=64, null=True, blank=True)

class Country(NamedObject):
    iso_code_3 = models.CharField(max_length=3)
    iso_code_2 = models.CharField(max_length=2)
    currency_iso_code_3 = models.CharField(max_length=3)

class Currency(NamedObject):
    iso_code_3 = models.CharField(max_length=3)
    iso_code_2 = models.CharField(max_length=2)
    iso_symbol = models.CharField(max_length=16)
    countries = models.ManyToManyField(Country)

class Type(NamedObject):
    target = models.CharField(max_length=128)

class SubType(NamedObject):
    target = models.CharField(max_length=128)

class Relationship(models.Model):
    rs_type = models.ForeignKey(Type, limit_choices_to={'target':'Relationship'})
    rs_target = models.ForeignKey(IdentifiableObject)

class ThirdParty(IdentifiableObject):
    third_type = models.ForeignKey(Type, limit_choices_to={'target':'ThirdParty'})
    relations = models.ManyToManyField(Relationship)

class FinancialAsset(IdentifiableObject):
    asset_type = models.ForeignKey(Type, limit_choices_to={'target':'ThirdParty'})
    relations = models.ManyToManyField(Relationship)
    
class AdditionalIdType(NamedObject):
    comment = models.TextField(null=True, blank=True)
    
class AdditionalId(models.Model):
    id_owner = models.ForeignKey(ThirdParty)
    id_type = models.ForeignKey(AdditionalIdType)
    id_value = models.CharField(max_length=128, null=True, blank=True)
    
    
class Track(IdentifiableObject):
    target = models.ForeignKey(NamedObject)
    track_type = models.ForeignKey(Type, limit_choices_to={'target':'Track'}, related_name='track_type')
    track_sub_type = models.ForeignKey(SubType, limit_choices_to={'target':'Track'}, null = True, related_name='track_sub_type')
    source = models.ForeignKey(Relationship, null=True)
    rank = models.IntegerField(default=0)
    is_percentage = models.BooleanField(default=False)
    is_yield = models.BooleanField(default=False)
    is_amount = models.ForeignKey(Currency, null=True, related_name='track_amount')

class TrackToken(models.Model):
    track = models.ForeignKey(Track)
    token_date = models.DateField()
    token_time = models.TimeField(default=datetime.time(0,0,0)) # Intraday only

class TrackTokenDouble(TrackToken):
    value = models.FloatField()
    
class TrackTokenInteger(TrackToken):
    value = models.IntegerField()

class TrackTokenBreakdown(TrackToken):
    target = models.ForeignKey(NamedObject)
    breakdown = models.FloatField()
    
class TrackTokenSet(TrackToken):
    values = models.ManyToManyField('AdditionalAttributeValue')

class AdditionalAttributeDefinition(NamedObject):
    comment = models.TextField(null=True, blank=True)
    type = models.ForeignKey(Type, limit_choices_to={'target':'AdditionalAttributeDefinition'}, related_name='aa_definition_type')
    entity_class = models.CharField(max_length=128)
    default_boolean = models.NullBooleanField(null=True)
    default_float = models.FloatField(null=True)
    default_integer = models.IntegerField(null=True)
    default_text = models.TextField(null=True, blank=True)
    default_target = models.ForeignKey(NamedObject, null=True, related_name='aa_definition_target')
    
class AdditionalAttributeValue(models.Model):
    target = models.ForeignKey(NamedObject)
    type = models.ForeignKey(AdditionalAttributeDefinition, related_name='aa_value_definition')
    value_boolean = models.NullBooleanField(null=True)
    value_float = models.FloatField(null=True)
    value_integer = models.IntegerField(null=True)
    value_text = models.TextField(null=True, blank=True)
    value_target = models.ForeignKey(NamedObject, null=True, related_name='aa_value_target')
    
class AttributeSet(NamedObject):
    definitions = models.ManyToManyField(AdditionalAttributeDefinition)