#coding=utf-8
from datetime import datetime, timedelta
import os
from django.conf import settings
from taggit.managers import TaggableManager
from photofile import get_filename, generate_thumb
from django.db import models
from metadata import get_metadata, metadata_fields, get_keywords, set_keywords
from django.contrib.auth.models import User

STATUS = (
    (0, 'Not processed'),
    (1, 'Under evaluation'),
    (2, 'Approved'),
    (3, 'Declined'),
    (4, 'Archived'),
)
STATUS_DICT = {}
for status_code, status_text in STATUS:
    STATUS_DICT[status_code] = status_text

class PhotoBase(models.Model):

    class Meta:
        abstract = True

    def thumbnail_url(self):
        complete_filename = get_filename(self)
        return '<img src="%s"/>' % generate_thumb(complete_filename, 100, 100, True)
    thumbnail_url.allow_tags = True
    thumbnail_url.short_description ="Photo"


class PhotoMetadata(PhotoBase):

    class Meta:
        abstract = True

    title = models.CharField(max_length = 200, blank = True, null = True, default='')
    description = models.TextField(blank = True, null = True, default='')
    photographer = models.CharField(max_length = 200, blank = True, null = True, default='')
    owner = models.ForeignKey(User)
    tags = TaggableManager(blank=True)

    # EXIF
    metadata_processed = models.NullBooleanField(default = False, null = True, blank = True)
    width = models.IntegerField(default = 0, null = True, blank = True)
    height = models.IntegerField(default = 0, null = True, blank = True)
    exif_date = models.DateTimeField(null = True, blank = True)
    camera_model = models.CharField(max_length = 50, blank = True, null = True)
    orientation = models.IntegerField(blank = True, null = True)
    exposure_time = models.FloatField(blank = True, null = True)
    fnumber = models.FloatField(blank = True, null = True)
    exposure_program = models.IntegerField(blank = True, null = True)
    iso_speed = models.IntegerField(blank = True, null = True)
    metering_mode = models.IntegerField(blank = True, null = True)
    light_source = models.IntegerField(blank = True, null = True)
    flash_used = models.IntegerField(blank = True, null = True)
    focal_length = models.FloatField(max_length = 50, blank = True, null = True)
    exposure_mode = models.IntegerField(blank = True, null = True)
    whitebalance = models.IntegerField(blank = True, null = True)
    focal_length_in_35mm = models.CharField(max_length = 50, blank = True, null = True)
    aperture = models.FloatField(blank = True, null = True)
    shutter_speed = models.FloatField(blank = True, null = True)

    # IPTC/XMP
    keywords = models.CharField(max_length=500, blank = True, null = True)
    headline = models.CharField(max_length=500, blank = True, null = True)
    caption = models.CharField(max_length=500, blank = True, null = True)
    copyright = models.CharField(max_length=500, blank = True, null = True)
    software = models.CharField(max_length=500, blank = True, null = True)

    # GEO/GPS-DATA
    longitude = models.FloatField(null = True, blank = True)
    latitude = models.FloatField(null = True, blank = True)
    altitude = models.FloatField(null = True, blank = True)

    # Stolen from https://github.com/nathanborror/django-basic-apps/blob/master/basic/media/models.py
    LICENSES = (
            ('http://creativecommons.org/licenses/by/2.0/',         'CC Attribution'),
            ('http://creativecommons.org/licenses/by-nd/2.0/',      'CC Attribution-NoDerivs'),
            ('http://creativecommons.org/licenses/by-nc-nd/2.0/',   'CC Attribution-NonCommercial-NoDerivs'),
            ('http://creativecommons.org/licenses/by-nc/2.0/',      'CC Attribution-NonCommercial'),
            ('http://creativecommons.org/licenses/by-nc-sa/2.0/',   'CC Attribution-NonCommercial-ShareAlike'),
            ('http://creativecommons.org/licenses/by-sa/2.0/',      'CC Attribution-ShareAlike'),
        )
    license = models.URLField(blank=True, choices=LICENSES)

    # Rating and status
#    RATINGS = (
#        (-1, 'Not rated'),
#        (0, 'Bad'),
#        (1, 'Poor'),
#        (2, 'Mediocre'),
#        (3, 'Ok'),
#        (4, 'Good'),
#        (5, 'Great'),
#        (6, 'Flawless'),
#    )
#    rating = models.IntegerField(choices=RATINGS, default=-1)
    
    status = models.IntegerField(choices=STATUS, default=0)

    # Misc
    mature_content = models.BooleanField(default=False)
    starred = models.BooleanField(default=False)
    private = models.BooleanField(default=True)

class AdvancedPhotoMetadata(PhotoMetadata):
    
    def populate_metadata(self):
        filename = get_filename(self)
        try:
            data = get_metadata(filename)
        except:
            return
        
        print "METADATA", data
        self.exif_date = data.get('exif_date')
        print "date", self.exif_date
        for key, value in data.items():
            if hasattr(self, key) and key in metadata_fields:
                print "Setting %s = %s" % (key, value)
                setattr(self, key, value)

    def save(self, force_insert=False, force_update=False):
        if not self.metadata_processed:
            super(PhotoMetadata, self).save()
            self.populate_metadata()
            self.metadata_processed = True
            super(PhotoMetadata, self).save()
        else:
            super(PhotoMetadata, self).save()

    def read_tags_from_photo(self):
        if hasattr(settings, 'READ_TAGS_FROM_PHOTO'):
            filename = get_filename(self)
            keywords = get_keywords(filename)
            print "Found keywords", keywords
            if keywords:
                for keyword in keywords:
                    self.tags.add(keyword)

    def write_tags_to_photo(self):
        if hasattr(settings, 'WRITE_TAGS_TO_PHOTO'):
            if settings.WRITE_TAGS_TO_PHOTO:
                print "Settings keywords", [k.name for k in self.tags.all()], get_filename(self)
                set_keywords(filename = get_filename(self), keywords=[k.name for k in self.tags.all()])

    def tags_url(self):
        return ','.join([k.name for k in self.tags.all()])
    tags_url.short_description ="Tags"



#    @classmethod
#    def taken_nearby(cls, lontitude, latitude):
#        query= """
#        SELECT *, 3956 * 2 * ASIN(SQRT(POWER(SIN((%s - LAT) * 0.0174532925 / 2), 2) + COS(%s * 0.0174532925) * COS(LAT * 0.0174532925) * POWER(SIN((%s - LON) * 0.0174532925 / 2), 2) )) as distance
#        from %s
#        having distance < 50
#        ORDER BY distance ASC
#        """ % (latitude, latitude, longitude, cls._meta.db_table)
#        return cls.objects.raw(query)
#
#    @classmethod
#    def close_in_time(cls, date, range_in_minutes=5, range_in_hours=None, range_in_days=None):
#        rng = range_in_minutes and timedelta(minutes=range_in_minutes) or \
#              range_in_hours and timedelta(hours=range_in_hours) or \
#              range_in_days and timedelta(days=range_in_days) or \
#              timedelta(1)
#
#        return cls.objects.filter(exif_date__range=(date - rng, date + rng))
##
##    @classmethod
##    def photosInRadius(cls, lat, long, radius = 10, use_km = True):
##        lng_min, lng_max, lat_min, lat_max = GeographicalLocation.calculateMinMaxRadius(lat, long, radius, use_km)
##        return Photo.objects.filter(longitude__gt = lng_min, longitude__lt = lng_max, latitude__gt = lat_min, latitude__lt = lat_max)
##
##    @classmethod
##    def isLatLongInRadiusOfCenter(cls, center_lat, center_long, perimeter_lat, perimeter_long, radius, use_km = True):
##        lng_min, lng_max, lat_min, lat_max = Location.inRadius(center_lat, center_long, radius, use_km)
##        return perimeter_long > lng_min and perimeter_long < lng_max and perimeter_lat > lat_min and perimeter_lat < lat_max
##
##    @classmethod
##    def calculateMinMaxRadius(cls, lat, long, radius, use_km = True):
##        # credits to : http://blog.fedecarg.com/2009/02/08/geo-proximity-search-the-haversine-equation/
##        if use_km:
##            radius = radius * 0.621371192;
##
##        lng_min = long - radius / abs(math.cos(math.radians(lat)) * 69)
##        lng_max = long + radius / abs(math.cos(math.radians(lat)) * 69)
##        lat_min = lat - (radius / 69)
##        lat_max = lat + (radius / 69)
##        return lng_min, lng_max, lat_min, lat_max
##
##    @classmethod
##    def LocationsInRadius(cls, lat, long, radius, use_km = True):
##        lng_min, lng_max, lat_min, lat_max = Location.calculateMinMaxRadius(lat, long, radius, use_km)
##        return Location.objects.filter(longitude__gt = lng_min, longitude__lt = lng_max, latitude__gt = lat_min, latitude__lt = lat_max)
