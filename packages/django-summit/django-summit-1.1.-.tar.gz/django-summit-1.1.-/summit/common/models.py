from django.db import models

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

class Menu(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    base_url = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    site = models.ForeignKey(Site)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __unicode__(self):
        return "%s" % self.name

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu)
    order = models.IntegerField()
    link_url = models.CharField(max_length=100, help_text='URL or URI to the content, eg /about/ or http://foo.com/')
    title = models.CharField(max_length=100)
    login_required = models.BooleanField(blank=True)
    
    def __unicode__(self):
        return "%s %s. %s" % (self.menu.slug, self.order, self.title)
