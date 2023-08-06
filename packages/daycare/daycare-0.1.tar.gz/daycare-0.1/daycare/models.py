from datetime import date, timedelta

from django.core.cache import cache
from django.db import models
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from daycare.cachekeys import (URL_HITS_LAST_MONTH_CACHEKEY,
                               URL_HITS_LAST_WEEK_CACHEKEY,
                               URL_HITS_ALL_CACHEKEY, URL_LAST_HIT_CACHEKEY,
                               URL_FIRST_HIT_CACHEKEY)
from daycare.utils import fetch

URL_HITS_CACHE_TIME = 60


class MissingURL(models.Model):
    """
    Represents single URL that somebody was trying to reach and got 404.
    """
    url = models.CharField(max_length=255, default='', unique=True)

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    # These 3 fields are kind of cache and are used only to let users sort
    # URLs in admin interface by these values
    # (MissingURLAdmin.get_queryset() updates them on each admin request)
    hits = models.IntegerField(default=0)
    hits_last_week = models.IntegerField(default=0)
    hits_last_month = models.IntegerField(default=0)

    class Meta:
        ordering = ('-hits',)

    def __unicode__(self):
        return self.url

    def has_redirect(self):
        return 'Yes' if Redirect.objects.filter(catch_url=self.url).count() else 'No'

    def get_hits_last_week(self):
        week_ago = date.today() - timedelta(days=7)
        return fetch(URL_HITS_LAST_WEEK_CACHEKEY % self.pk,
                     self.urlhit_set.filter(date__gte=week_ago).count(),
                     cache_time=URL_HITS_CACHE_TIME)

    def get_hits_last_month(self):
        month_ago = date.today() - timedelta(days=30)
        return fetch(URL_HITS_LAST_MONTH_CACHEKEY % self.pk,
                     self.urlhit_set.filter(date__gte=month_ago).count(),
                     cache_time=URL_HITS_CACHE_TIME)

    def get_hits(self):
        return fetch(URL_HITS_ALL_CACHEKEY % self.pk,
                     self.urlhit_set.all().count(),
                     cache_time=URL_HITS_CACHE_TIME)

    def last_hit(self):
        try:
            return fetch(URL_LAST_HIT_CACHEKEY % self.pk,
                         self.urlhit_set.all().order_by('-date')[0].date,
                         cache_time=URL_HITS_CACHE_TIME)
        except IndexError:
            pass
        return ''

    def first_hit(self):
        try:
            return fetch(URL_FIRST_HIT_CACHEKEY % self.pk,
                         self.urlhit_set.all().order_by('date')[0].date,
                         cache_time=URL_HITS_CACHE_TIME)
        except IndexError:
            pass
        return ''



class URLHit(models.Model):
    """
    Remembers a single bad URL hit. It is used for stats.
    """
    url = models.ForeignKey(MissingURL)
    date = models.DateField(auto_now_add=True)

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return "%s on %s" % (self.url, self.date)

    def save(self, *args, **kwargs):
        #reset cached counters after saving new URLHit
        cache.delete_many([URL_LAST_HIT_CACHEKEY % self.url.pk,
                          URL_HITS_ALL_CACHEKEY % self.url.pk,
                          URL_HITS_LAST_MONTH_CACHEKEY % self.url.pk,
                          URL_HITS_LAST_WEEK_CACHEKEY % self.url.pk, ])

        super(URLHit, self).save(*args, **kwargs)


class Redirect(models.Model):
    """
    Can either be a
    - proposition/draft of redirect (suggested to user by this software),
    - redirect itself or
    - disabled redirect.
    """
    STATUS_DRAFT, STATUS_ACTIVE, STATUS_DISABLED = 'Draft', 'Active', 'Disabled'
    REDIRECT_STATUSES = (
         (STATUS_DRAFT, 'Draft'),
         (STATUS_ACTIVE, 'Active'),
         (STATUS_DISABLED, 'Disabled'),
    )

    catch_url = models.CharField(max_length=255, default='', unique=True)
    redirect_url = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=20,
                              choices=REDIRECT_STATUSES,
                              default=STATUS_DRAFT)
    created_automatically = models.BooleanField(default=False)

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return "%s to %s" % (self.catch_url, self.redirect_url)

    def get_missing_url(self):
        return MissingURL.objects.get(url=self.catch_url)

    def get_hits_all(self):
        if self.created_automatically and self.status != self.STATUS_ACTIVE:
            return self.get_missing_url().hits()
        return '-'

    def hits_last_week(self):
        if self.created_automatically and self.status != self.STATUS_ACTIVE:
            return self.get_missing_url().hits_last_week()
        return '-'

    def hits_last_month(self):
        if self.created_automatically and self.status != self.STATUS_ACTIVE:
            return self.get_missing_url().hits_last_month()
        return '-'


class PageURLTrack(models.Model):
    """
    Keeps track of cms Page absolute URL changes.
    It is used to automatically make proposition of redirect if URL changes.

    Every time Page absolute URL changes, new PageURLTrack object is created (pre/post save).
    This lets to keep track which redirects should be updated with new URL
    (all previous Page urls should point to new URL).
    """

    page_id = models.IntegerField(default=0)
    last_url = models.CharField(max_length=255, default='')

    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return "page %s, url %s" % (self.page_id, self.last_url)
