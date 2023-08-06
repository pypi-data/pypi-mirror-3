# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from intranet.widgets import PhoneField, SiretField

class Field(models.Model):
    name = models.CharField(_('name'), max_length=50)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _('field')
        ordering = ['name']

class Prospect(models.Model):

    company_name = models.CharField(_('company name'), max_length=100)
    field = models.ForeignKey(Field, related_name="prospects")
    siret_code = SiretField(_('SIRET code'), blank=True)
    
    # title (Mr, Mrs, Ms). Maybe a title can be longer in other languages?
    title = models.CharField(_('title'), max_length=5, blank=True)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    profession = models.CharField(_('profession'), max_length=100, blank=True)
    e_mail = models.EmailField(_('e-mail'), blank=True)
    phone_number = PhoneField(_('phone number'), help_text=_("Please enter a phone number in the form: 03 90 87 65 43 or +33.390876543"), blank=True)
    
    street = models.CharField(_('street'), max_length=100, blank=True)
    # A postal code can have numbers and letters, and can be quite long, depending on the state.
    # When the code is split in two with a dash, we don't want to save the dash in the database.
    postal_code = models.CharField(_('postal code'), max_length=10)
    city = models.CharField(_('city'), max_length=50)
    
    def __unicode__(self):
        return u'%s' % self.company_name
    
    class Meta:
        verbose_name = _('prospect')
        ordering = ['company_name']


