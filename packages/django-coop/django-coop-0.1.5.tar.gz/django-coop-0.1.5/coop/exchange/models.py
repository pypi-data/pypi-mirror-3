# -*- coding:utf-8 -*-
from django.db import models
from django_extensions.db import fields as exfields
from django.utils.translation import ugettext_lazy as _
from extended_choices import Choices
import datetime
from django.core.urlresolvers import reverse
from decimal import Decimal
from django.conf import settings

if "coop_geo" in settings.INSTALLED_APPS :
    from coop_geo.models import Area, Location


MODALITIES = Choices(
    ('GIFT',    1,  _(u'Gift')),
    ('TROC',    2,  _(u'Free exchange')),
    ('CURR',    3,  _(u'Monetary exchange')),
)
UNITS = Choices(
    ('EURO',    1,  _(u'€')),
    ('SELH',    2,  _(u'Hours')),
    ('PEZ',     3,  _(u'PEZ')),    
)

class BasePaymentModality(models.Model):
    exchange = models.ForeignKey('coop_local.Exchange', verbose_name=_(u'exchange'),related_name='modalities')
    modality = models.PositiveSmallIntegerField( _(u'exchange type'),blank=True,
                                                    choices=MODALITIES.CHOICES,
                                                    default=MODALITIES.CURR)
    amount = models.DecimalField(_(u'amount'),max_digits=12, decimal_places=2, default=Decimal(0.00),blank=True)
    unit = models.PositiveSmallIntegerField(_(u'unit'), blank=True, null=True, choices=UNITS.CHOICES)
    
    def __unicode__(self):
        if(self.modality in [1,2]):
            return unicode(MODALITIES.CHOICES_DICT[self.modality])
        elif(self.modality == 3 and self.amount > 0 and not self.unit == None):
            return unicode( "%s %s"%(self.amount, unicode(UNITS.CHOICES_DICT[self.unit])) )
        elif(self.modality == 3):
            return unicode(_(u'Price unknown'))
    def save(self, *args, **kwargs):
        if not self.modality == 3:
            self.amount = Decimal(0.00)
            self.unit = None
        super(BasePaymentModality, self).save(*args, **kwargs) 
                
    class Meta:
        abstract = True
        verbose_name = _(u'Payment modality')
        verbose_name_plural = _(u'Payment modalities')


EXCHANGE = Choices(
    ('P_OFFER',   1,  _(u'Product Offer')),
    ('S_OFFER',   2,  _(u'Service Offer')),
    ('P_NEED',    3,  _(u'Product Need')),
    ('S_NEED',    4,  _(u'Service Need')),
    ('MUTU',    7,  _(u'Mutualization')),#3
    ('COOP',    8,  _(u'Cooperation, partnership')),#5
    ('QA',      9,  _(u'Question')),#6
)

class BaseExchange(models.Model):
    title = models.CharField(_('title'),blank=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True)
    organization = models.ForeignKey('coop_local.Organization',blank=True,null=True,verbose_name='publisher', related_name='exchange')
    person = models.ForeignKey('coop_local.Person',blank=True,null=True,editable=False,verbose_name=_(u'person'))
    etype = models.PositiveSmallIntegerField( _(u'exchange type'),choices=EXCHANGE.CHOICES)
    permanent = models.BooleanField(_(u'permanent'),default=True)
    expiration = models.DateField(_(u'expiration'),blank=True,null=True)
    slug = exfields.AutoSlugField(populate_from='title')
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    
    uri = models.CharField(_(u'main URI'),blank=True, max_length=250, editable=False)
    author_uri = models.CharField(_(u'author URI'),blank=True, max_length=200, editable=False)
    publisher_uri = models.CharField(_(u'publisher URI'),blank=True, max_length=200, editable=False)

    uuid = exfields.UUIDField() #nécessaire pour URI ?
    
    if "coop_geo" in settings.INSTALLED_APPS :
        location = models.ForeignKey(Location,null=True,blank=True,verbose_name=_(u'location'))
        area = models.ForeignKey(Area,null=True,blank=True,verbose_name=_(u'area'))    
    
    def __unicode__(self):
        return unicode(self.title)
    def get_absolute_url(self):
        return reverse('annonce_detail', args=[self.uuid])
        
    #TODO assign the record to the person editing it (form public) and provide an A-C choice in admin

    class Meta:
        abstract = True
        verbose_name = _(u'Exchange')
        verbose_name_plural = _(u'Exchanges')
       

    
class BaseTransaction(models.Model):
    origin = models.ForeignKey('coop_local.Exchange',related_name='origin', verbose_name=_(u'origin'))
    destination = models.ForeignKey('coop_local.Exchange',related_name='destination', verbose_name=_(u'destination'))
    title = models.CharField(_('title'),blank=True,max_length=250)
    description = models.TextField(_(u'description'),blank=True)
    created = exfields.CreationDateTimeField(_(u'created'),null=True)
    modified = exfields.ModificationDateTimeField(_(u'modified'),null=True)
    uuid = exfields.UUIDField() #nécessaire pour URI ?
    
    class Meta:
        abstract = True
        verbose_name = _(u'Transaction')
        verbose_name_plural = _(u'Transactions')