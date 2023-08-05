from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.models import PhoneNumberField

#from articles.models import Article
from multiblogs.models import Blog
from onec_utils.utils import unique_slugify
from onec_utils.models import USAddressPhoneMixin
from photologue.models import Photo, Gallery
from markup_mixin.models import MarkupMixin
from django_extensions.db.models import TitleSlugDescriptionModel, TimeStampedModel
from django_extensions.db.fields import AutoSlugField
from classroom.managers import TeacherManager, StaffManager, ConsultantManager, ActiveManager

class School(MarkupMixin, TitleSlugDescriptionModel, USAddressPhoneMixin):
    """
    School model class.
    
    Manages a school.

    """
    principal=models.ForeignKey('Staff', blank=True, null=True, related_name='principal')
    photo=models.ImageField(_('Photo'), blank=True, null=True, upload_to='classroom/school/')
    primary=models.BooleanField(_('Primary'), default=False, 
            help_text='Is this the sites primary, or only school?')
    email=models.EmailField(_('Email'), blank=True, null=True)
    url=models.CharField(_('URL'), blank=True, null=True, max_length=255)
    po_box=models.IntegerField(_('P.O. Box'), blank=True, null=True, max_length=4)
    fax=PhoneNumberField(_('Fax'), blank=True, null=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)
        
    class Meta:
        verbose_name=_('School')
        verbose_name_plural=_('Schools')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'

  
    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('cl-school-detail', None, {'slug': self.slug})

class Position(MarkupMixin, TitleSlugDescriptionModel, TimeStampedModel):
    """
    Position model, but not like homework position, but rather teacher position.
    
    """
    abbreviated_title=models.CharField(_('Abbreviated title'), blank=True, null=True, max_length=40)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)

    class Meta:
        verbose_name=_('Position')
        verbose_name_plural=_('Positions')

    class markupoptions:
        source_field = 'description'
        rendered_field = 'rendered_description'
  
    def __unicode__(self):
        return u'%s' % self.title

    @property
    def shortened_title(self):
        if self.abbreviated_title: return self.abbreviated_title
        else: return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('cl-position-detail', None, {'slug': self.slug})

class StaffType(TimeStampedModel, TitleSlugDescriptionModel):
    """
    Staff Type model.

    """

    class Meta:
        verbose_name=_('Staff type')
        verbose_name_plural=_('Staff types')

    def __unicode__(self):
        return u'%s' % self.title

class Website(TimeStampedModel, TitleSlugDescriptionModel):
    """
    Website model for keeping track of teacher websites
    """
    url=models.CharField(_('URL Address'), max_length=255)

    class Meta:
        verbose_name=_('Website')
        verbose_name_plural=_('Websites')

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('cl-website-detail', None, {'slug': self.slug})

class Staff(MarkupMixin, TimeStampedModel):
    """
    Staff model class.
    
    """
    name=models.CharField(_('Name'), max_length=100)
    title=models.CharField(_('Title'), blank=True, null=True, max_length=20)
    slug=AutoSlugField(_('Slug'), populate_from='name')
    school=models.ForeignKey(School)
    mug=models.ImageField(_('Mug'), blank=True, null=True, upload_to='staff/mugs/')
    photo=models.ImageField(_('Photo'), blank=True, null=True, upload_to='staff/photos/')
    user=models.ForeignKey(User, blank=True, null=True)
    email=models.EmailField(_('Email'), max_length=200, blank=True, null=True)
    active=models.BooleanField(_('Active'), 
            help_text='Is this staff member currently active?', default=False)
    type=models.ForeignKey(StaffType)
    bio=models.TextField(_('Biography'), blank=True, null=True)
    order=models.IntegerField(_('Order'), blank=True, null=True)
    rendered_bio=models.TextField(_('Rendered biography'), blank=True, null=True)
    positions=models.ManyToManyField(Position, blank=True, null=True)
    gcal=models.TextField(_('Google Calendar Embed'), blank=True, null=True)
    websites=models.ManyToManyField(Website, blank=True, null=True)
    blog=models.ForeignKey(Blog, blank=True, null=True)

    objects = models.Manager()
    active_objects=ActiveManager()
    teacher_objects=TeacherManager()
    staff_objects=StaffManager()
    consultant_objects=ConsultantManager()
        
    class Meta:
        verbose_name=_('Staff')
        verbose_name_plural=_('Staff')
        ordering=('order',)

    class MarkupOptions:
        source_field = 'bio'
        rendered_field = 'rendered_bio'

    @property
    def first_name(self):
        return self.name.split(' ')[0]

    def last_name(self):
        return " ".join(self.name.split(' ')[1:])
  
    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('cl-staff-detail', None, {'slug': self.slug})



        
