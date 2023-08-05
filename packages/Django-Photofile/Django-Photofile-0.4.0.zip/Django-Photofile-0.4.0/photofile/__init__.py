#coding=utf-8
import os
from PIL import Image
from PIL.ExifTags import TAGS
from django.core.cache import cache
from django.conf import settings

from metadata import get_exif

def get_filename(p):
    if hasattr(p, 'photo'):
        if hasattr(p.photo, 'name'):
            return p.photo.name
        else:
            return p.photo
    elif hasattr(p, 'image'):
        if hasattr(p.image, 'name'):
            return p.image.name
        else:
            return p.image

    elif hasattr(p, 'unique_filename'):
        return p.unique_filename
    elif hasattr(p, 'complete_filename'):
        return p.complete_filename
    elif hasattr(p, 'filename'):
        return p.filename


def generate_thumb(complete_filename, width, height, do_crop, alternative_thumbnail_name=False):
    fname, ext = os.path.splitext(os.path.basename(complete_filename))
    if alternative_thumbnail_name:
        fname = alternative_thumbnail_name
    resized_image = '%s_%sx%s%s%s' % (fname, width, height, do_crop and '_crop' or '',ext)
    cached_filename = cache.get(resized_image, None)
    if cached_filename:
        return cached_filename

    if not os.path.exists(complete_filename):
        return 'inputfile does not exists'

    #static_folder = len(settings.STATICFILES_DIRS) and settings.STATICFILES_DIRS[0] or settings.STATIC_ROOT

    thumb_dir = os.path.join(settings.STATIC_ROOT, 'thumbs')
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)

    output = os.path.join(thumb_dir, resized_image)
    final_url = "%sthumbs/%s" % (settings.STATIC_URL, resized_image)
    cache.set(resized_image, final_url, 30)
    if not os.path.exists(output):
        resize_image(complete_filename, output, width, height, crop=do_crop)
    return final_url

def resize_image(source_file, target_file, width, height, crop=False):
    """
    Resizes an image specified by source_file and writes output to target_file.
    Will read EXIF data from source_file, look for information about orientation
    and rotate photo if such info is found.
    """
    image = Image.open(source_file)
    orientation = 0
    try:
        for tag, value in image._getexif().items():
            if TAGS.get(tag, tag) == 'Orientation':
                orientation = value
    except:
        orientation = None

    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    if not crop:
        image.thumbnail((width, height), Image.ANTIALIAS)
    else:
        src_width, src_height = image.size
        src_ratio = float(src_width) / float(src_height)
        dst_width, dst_height = width, height
        dst_ratio = float(dst_width) / float(dst_height)

        if dst_ratio < src_ratio:
            crop_height = src_height
            crop_width = crop_height * dst_ratio
            x_offset = int(float(src_width - crop_width) / 2)
            y_offset = 0
        else:
            crop_width = src_width
            crop_height = crop_width / dst_ratio
            x_offset = 0
            y_offset = int(float(src_height - crop_height) / 3)
        image = image.crop((x_offset, y_offset, x_offset+int(crop_width), y_offset+int(crop_height)))
        image = image.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)

    # rotate according to orientation stored in exif-data:
    if orientation:
        if orientation == 2:
            # Vertical Mirror
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180°
            image = image.transpose(Image.ROTATE_180)
        elif orientation == 4:
            # Horizontal Mirror
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            # Horizontal Mirror + Rotation 270°
            image = image.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)
        elif orientation == 6:
            # Rotation 270°
            image = image.transpose(Image.ROTATE_270)
        elif orientation == 7:
            # Vertical Mirror + Rotation 270°
            image = image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
        elif orientation == 8:
            # Rotation 90°
            image = image.transpose(Image.ROTATE_90)

    image.save(target_file)
