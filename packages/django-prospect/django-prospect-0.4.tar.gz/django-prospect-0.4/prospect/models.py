# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import date

from intranet.widgets import PhoneField, SiretField


class Field(models.Model):
    name = models.CharField(_('name'), max_length=50)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _('field')
        verbose_name_plural = _('fields')
        ordering = ['name']


class Prospect(models.Model):

    ### Company information ###
    company_name = models.CharField(_('company name'), max_length=100)
    field = models.ForeignKey(Field, related_name='prospects', null=True, blank=True)
    siret_code = SiretField(_('SIRET code'), blank=True)
    
    ### Information about the person ###
    # title (Mr, Mrs, Ms). Maybe a title can be longer in other languages?
    title = models.CharField(_('title'), max_length=5, blank=True)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    profession = models.CharField(_('profession'), max_length=100, blank=True)
    e_mail = models.EmailField(_('e-mail'), blank=True)
    phone_number = PhoneField(_('phone number'), help_text=_('Please enter a phone number in the form: 03 90 87 65 43 or +33.390876543'), blank=True)
    
    ### Geographic information ###
    street = models.CharField(_('street'), max_length=100, blank=True)
    # A postal code can have numbers and letters, and can be quite long, depending on the state.
    # When the code is split in two with a dash, we don't want to save the dash in the database.
    postal_code = models.CharField(_('postal code'), max_length=10)
    city = models.CharField(_('city'), max_length=50)
    
    # In order not to display 'None'
    def field_display(self):
        return self.field and self.field or u''
    
    field_display.short_description = _('field')
    
    @property
    def last_activities(self):
        return self.activities.all()[:5]
        
    def __unicode__(self):
        return u'%s' % self.company_name
    
    class Meta:
        verbose_name = _('prospect')
        ordering = ['company_name']


class Activity(models.Model):

    contact = models.ForeignKey(Prospect, related_name='activities')
    subject = models.CharField(_('subject'), max_length=50)    
    TYPES = (
        ('e', _(u'e-mail')),
        ('p', _(u'phone call')),
        ('m', _(u'meeting')),
        ('f', _(u'fax')),
    )
    activity_type = models.CharField(_('activity type'), max_length=1, choices=TYPES)
    DIRECTIONS = (
        ('i', _(u'incoming')),
        ('o', _(u'outgoing')),
    )
    # Translators: direction of a phone call or an e-mail: "incoming" or "outgoing"
    direction = models.CharField(
        _('direction'),
        max_length = 1,
        choices = DIRECTIONS,
        blank = True,
        help_text = _(u'In the case of a phone call, an e-mail or a fax, choose the direction of the message.'),
    )
    datetime = models.DateTimeField(
        _('date and time'),
        help_text = _(u'Please insert a date and time in the form "DD/MM/YYYY HH:MM".'),
    )
    duration = models.TimeField(
        _('duration'),
        help_text = _(u'In the case of a phone call or a meeting, you can precise the duration, in the form "HH:MM:SS".'),
        blank = True,
        null = True,
    )
    comments = models.TextField(_('comments'), blank=True)
    is_important = models.BooleanField(_('important'), help_text=_(u'Check that box if you want to mark this activity as an important one.'))
    
    # TODO Enable ordering for callable attributes
    def activity_type_display(self):
        found = True
        if self.activity_type == 'e':
            icon_name = 'envelope'
        elif self.activity_type == 'p':
            icon_name = 'headphones'
        elif self.activity_type == 'm':
            icon_name = 'user'
        elif self.activity_type == 'f':
            icon_name = 'print'
        else:
            found = False
        if found:
            return u'<i class="icon-%s"></i>&nbsp;%s' % (icon_name, self.get_activity_type_display())
        else:
            return u''
    
    activity_type_display.short_description = _('activity type')
    
    def direction_display(self):
        found = True
        if self.direction == 'i':
            icon_name = 'arrow-down'
        elif self.direction == 'o':
            icon_name = 'arrow-up'
        else:
            found = False
        if found:
            return u'<i class="icon-%s"></i>&nbsp;%s' % (icon_name, self.get_direction_display())
        else:
            return u''
    
    direction_display.short_description = _('direction')
    
    # In order not to display 'None'
    def duration_display(self):
        return self.duration and self.duration.strftime('%H:%M') or u'--:--'
    
    duration_display.short_description = _('duration')
    
    # Not to display the entire comments
    def comments_display(self):
        if len(self.comments) <= 50:
            return self.comments
        else:
            return u'%s...' % self.comments[:50]
    
    comments_display.short_description = _('comments')
    
    def datetime_display(self):
        return self.datetime.strftime('%d/%m/%y %H:%M')
    
    datetime_display.short_description = _('date and time')
    
    def is_important_display(self):
        return self.is_important and u'<i class="icon-exclamation-sign"></i>' or u''
    
    is_important_display.short_description = u'<i class="icon-exclamation-sign"></i>'
    
    def __unicode__(self):
        return u'%s' % self.subject
    
    class Meta:
        verbose_name = _('activity')
        verbose_name_plural = _('activities')
        ordering = ['-datetime']

