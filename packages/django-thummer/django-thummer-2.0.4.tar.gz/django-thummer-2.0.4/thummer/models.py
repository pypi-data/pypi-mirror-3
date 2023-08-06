# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import get_storage_class
from django.db import models
from pyvirtualdisplay import Display
from selenium import webdriver
from sorl.thumbnail import ImageField, get_thumbnail as sorl_thumbnail
from thummer import settings, tasks, utils
from thummer.managers import QuerySetManager
import base64

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5


class WebpageSnapshot(models.Model):
    """Model representing a webpage snapshot."""
    url = models.URLField(db_index=True)
    image = ImageField(editable=False, storage=settings.STORAGE,
        upload_to=settings.UPLOAD_PATH, null=True)
    capture_width = models.IntegerField(default=1680, editable=False)
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    captured_at = models.DateTimeField(editable=False, null=True)
    objects = QuerySetManager()
    
    class Meta(object):
        get_latest_by = 'captured_at'
        ordering = ['-captured_at']
    
    class QuerySet(models.query.QuerySet):
        def valid(self):
            captured_after = datetime.now() - settings.VALID_FOR
            return self.filter(
                models.Q(captured_at__gte=captured_after)|
                models.Q(captured_at__isnull=True))
    
    def __unicode__(self):
        return self.url
    
    def _capture(self):
        """Save snapshot image of webpage, and set captured datetime."""
        display = Display(visible=0, size=self._get_capture_resolution())
        display.start()
        browser = webdriver.Firefox()
        browser.get(self.url)
        self.captured_at = datetime.now()
        png = browser.get_screenshot_as_base64()
        browser.quit()
        display.stop()
        self.image.save(self._generate_filename(),
            ContentFile(base64.decodestring(png)))
        return True
    
    def _generate_filename(self):
        """Returns a unique filename base on the url and created datetime."""
        assert self.captured_at
        datetime_string = unicode(self.captured_at)
        hexdigest = md5(datetime_string + self.url).hexdigest()
        return '%s/%s.png' %(settings.UPLOAD_PATH, hexdigest)
    
    def _get_capture_resolution(self):
        return (self.capture_width, int((self.capture_width/16.0)*10))
    
    def get_absolute_url(self):
        return self.image and self.image.url
    
    def get_image(self):
        return self.image or self.get_placeholder_image()
    
    def get_placeholder_image(self):
        storage_class = get_storage_class(settings.STATICFILES_STORAGE)
        storage = storage_class()
        placeholder = storage.open(settings.PLACEHOLDER_PATH)
        image = ImageFile(placeholder)
        image.storage = storage
        return image
    
    def get_thumbnail(self, geometry_string, **kwargs):
        """A shortcut for sorl thumbnail's ``get_thumbnail`` method."""
        for key, value in settings.THUMBNAIL_DEFAULTS.items():
            kwargs.setdefault(key, value)
        if not self.image:
            # Placeholder images
            kwargs.update(settings.PLACEHOLDER_DEFAULTS)
        if geometry_string is None:
            # We have to use django's ImageFile, as sorl-thumbnail's ImageField
            # extends File and not ImageFile, so width property is not
            # available.
            image = ImageFile(self.get_image().file)
            geometry_string = '%s' %(image.width)
        return sorl_thumbnail(self.get_image(), geometry_string,  **kwargs)
    
    def save(self, *args, **kwargs):
        new = not self.pk
        super(WebpageSnapshot, self).save(*args, **kwargs)
        if new:
            if settings.QUEUE_SNAPSHOTS:
                tasks.capture.delay(pk=self.pk)
            else:
                tasks.capture(pk=self.pk)

models.signals.pre_delete.connect(utils.delete_image, sender=WebpageSnapshot)

