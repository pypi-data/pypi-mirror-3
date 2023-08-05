Photofile
=========

Version : 0.4.0
Author : Thomas Weholt <thomas@weholt.org>
License : Modified BSD
WWW : https://bitbucket.org/weholt/django-photofile
Status : Beta


About
-----
* Templatetags for thumbnail generation, supports automatic rotation based on EXIF.Orientation.
* An abstract model for photos, handling extraction of EXIF-metadata.
* Next planned feature: tagging - reading and writing tags to and from photo metadata (IPTC/XMP).

Changelog
---------
0.4.0 - Added decorator for finding screen resolution. See How-section for example.


How
---
    <img src="{% generate_thumbnail imagefile 100x100 crop %}"/>

Provides a templatetag called generate_thumbnail which takes two or three parameters:

Param #1 : an object (imagefile), like a model instance, with a property/field called unique_filename, complete_filename or filename.
Photofile will check in that order.

Param #2: resolution, specified as <width>x<height>, like 320x280.

Param #3: optional "crop" - which will enforce cropping of the photo.

The thumbnail will be written in a dir called "thumbs" in your STATICFILES_DIRS or STATIC_ROOT. If no dir exists
called thumbs, it will be created.

The generated thumbnail will be named <filename>_<width>x<height>.<extension>. When cropping is used it will be named
<filename>_<width>x<height>_crop.<extension>. For instance, thumbnail for test.jpg in resolution 200x300 will be named
test_200x300.jpg.

Photofile will try to use caching if enabled, but it caches the url to the thumbnail, not the image itself so it's not
very efficient yet.

NB! It's highly recommended to have some way of ensuring that the filename given to photofile is unique. That's why it will
look for a property called unique_filename first.

To use the abstract model, do something like this::

    from django.db import models
    from photofile.models import PhotoMetadata

    class Photo(PhotoMetadata):
        image = models.ImageField(upload_to=settings.STATIC_DATA)
        title = models.CharField(max_length=100)

        def __unicode__(self):
            if self.width and self.height:
                return "%s (%sx%s)" % (self.title, self.width, self.height)
            else:
                return self.title

STATIC_DATA mentioned above is for testing only and can be defined in settings.py like so::

    import tempfile
    import os
    STATIC_DATA = os.path.join(tempfile.gettempdir(), 'staticdata')
    if not os.path.exists(STATIC_DATA):
        os.makedirs(STATIC_DATA)

    MEDIA_ROOT = STATIC_DATA


    STATICFILES_DIRS = (
        STATIC_DATA,
    )

When uploading a photo and saving it for the first time EXIF-metadata will be extracted and stored in the db. These EXIF-properties
are currently available, but longitude, latitude and altitude is not implemented yet:

* width
* height
* longitude
* latitude
* altitude
* exif_date
* camera_model
* orientation
* exposure_time
* fnumber
* exposure_program
* iso_speed
* metering_mode
* light_source
* flash_used
* focal_length
* exposure_mode
* whitebalance
* focal_length_in_35mm

The source contains an example project with more details on how to implement a suitable admin.py, some templates etc.

New in 0.4.0:

Photofile can detect screen resolution using a decorator, like so:

    from django.http import HttpResponseRedirect, HttpResponse
    from photofile.decorators import provide_screen_info

    @provide_screen_info
    def index(request):
         return HttpResponse("%sx%s" % (request.session.get('screen_width'), request.session.get('screen_height')))

You also need to add the photofile.urls:

    from django.conf.urls.defaults import patterns, include, url
    import photofile

    urlpatterns = patterns('',
        url(r'^default.html$', 'testme.views.index'),
    )
    urlpatterns += photofile.urls.urlpatterns;


This also makes it possible for photofile to automatically generate maximized thumbnails depending on the screen resolution:

    <img src="{% generate_thumbnail imagefile max %}"/>

using the max option for resolution.


Why another thumbnail app for django?
-------------------------------------
I've looked at sorl-thumbnail and others, and initially I wanted to use an existing project, but none of them supported
automatic rotation based on EXIF.Orientation.

Installation
------------
* Alternative a) pip install django-photofile.
* Alternative b) download source, unpack and do python setup.py install.
* Alternative c) hg clone https://bitbucket.org/weholt/django-photofile and do python setup.py install.

Usage
-----
In settings.py:
* Add 'photofile' to your INSTALLED_APPS.
* Set up caching if you want.
* Add a dir to your STATICFILES_DIRS or set STATIC_ROOT.

In your template:
     {% load photofile_tags %}

     <img src="{% generate_thumbnail imagefile 200x300 %}"/>
or
     <img src="{% generate_thumbnail imagefile 100x100 crop %}"/>

Where imagefile is an object with at a property/field called:
* unique_filename or
* complete_filename or
* filename

Resolution is specified as <width>x<height>, for instance 640x480 and if you want to crop the photo add crop as shown in
the example over.

Requirements
------------
* django
* PIL
* pyexiv2
* django-taggit