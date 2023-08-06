# -*- coding:utf-8 -*-
# author: bcabezas@apsl.net

from django.db import models

from cms.models import CMSPlugin
from easy_thumbnails.files import get_thumbnailer
from django.contrib.staticfiles.finders import find as staticfiles_find
import os


class SliderImage(models.Model):
    """Image class that user django-filer"""
    name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="nivoslider")
    order = models.PositiveIntegerField(default=100)

    class Meta:
        verbose_name = u'Image'
        verbose_name_plural = u'Images'
        ordering = ('order', 'name',)

    def __unicode__(self):
        if self.name:
            name = self.name
        else:
            try:
                name = self.image.file.name.split("/")[-1]
            except:
                name = unicode(self.image)
        return name

    def thumb(self):
        thumbnail_options = dict(size=(92, 37), crop=True)
        url = get_thumbnailer(self.image).get_thumbnail(thumbnail_options).url
        return '<img src="%s">' % url
    thumb.allow_tags = True
    thumb.short_description = 'Image'


class SliderAlbum(models.Model):
    """Image gallery for slider"""
    name = models.CharField(max_length=150)
    images = models.ManyToManyField(SliderImage, blank=True)

    class Meta:
        verbose_name = u'Slider Album'
        verbose_name_plural = u'Slider Albums'

    def __unicode__(self):
        return self.name


EFFECTS = """
    sliceDown
    sliceDownLeft
    sliceUp
    sliceUpLeft
    sliceUpDown
    sliceUpDownLeft
    fold
    fade
    random
    slideInRight
    slideInLeft
    boxRandom
    boxRain
    boxRainReverse
    boxRainGrow
    boxRainGrowReverse
"""
EFFECT_CHOICES = ((e, e) for e in EFFECTS.split())


def find_themes():
    themedirs = staticfiles_find("nivo/themes/", all=True)
    for dir in themedirs:
        for theme in os.listdir(dir):
            yield theme

THEME_CHOICES = ((t, t) for t in set(find_themes()))


class SliderPlugin(CMSPlugin):
    title = models.CharField('title', max_length=255, null=True, blank=True)
    album = models.ForeignKey(SliderAlbum)
    theme = models.CharField(choices=THEME_CHOICES, max_length=50,
                             default="default")
    effect = models.CharField(choices=EFFECT_CHOICES, max_length=50,
                              default="random")
    anim_speed = models.PositiveIntegerField(default=500,
                                             help_text="Animation Speed (ms)")
    pause_time = models.PositiveIntegerField(default=3000,
                                             help_text="Pause time (ms)")
    width = models.PositiveIntegerField(null=True, blank=True,
                                        help_text="Width of the plugin (px)")
    height = models.PositiveIntegerField(null=True, blank=True,
                                         help_text="Height of the plugin (px)")

    def __unicode__(self):
        if self.title:
            return self.title
        return self.album.name

    search_fields = ('title', 'album__name',)
