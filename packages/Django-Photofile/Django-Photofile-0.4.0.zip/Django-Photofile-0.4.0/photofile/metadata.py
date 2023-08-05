#coding=utf-8
import os
import time
import datetime
import re
import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PIL import IptcImagePlugin

try:
    import pyexiv2
    PYEXIV2_SUPPORT = True
except ImportError:
    PYEXIV2_SUPPORT = False

# Credits http://eran.sandler.co.il/2011/05/20/extract-gps-latitude-and-longitude-data-from-exif-using-python-imaging-library-pil/
def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def _fractToSimple(frac):
    if not frac:
        return None
    try:
        f,n = frac
        return round(float(f) / float(n), 3)
    except Exception, e:
        return None

def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_keywords(filename):
    if not PYEXIV2_SUPPORT:
        metadata = get_exif(filename)
        return metadata.get('keywords', [])
    
    metadata = pyexiv2.metadata.ImageMetadata(filename)
    metadata.read()
    key = 'Iptc.Application2.Keywords' # XMP keywords?
    try:
        return [s.strip() for s in metadata[key].raw_value]
    except KeyError:
        return []

def set_keywords(filename, keywords):
    if not PYEXIV2_SUPPORT or not keywords:
        return

    metadata = pyexiv2.metadata.ImageMetadata(filename)
    metadata.read()
    key = 'Iptc.Application2.Keywords' # XMP keywords?
    try:
        old_keywords = [s.strip() for s in metadata[key].raw_value]
    except KeyError:
        old_keywords = []

    for keyword in old_keywords:
        if not keyword in keywords:
            keywords.append(keyword)

    metadata[key] = keywords#pyexiv2.ExifTag(key, 
    metadata.write()

# http://www.blog.pythonlibrary.org/2010/03/28/getting-photo-metadata-exif-using-python/
def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        #print "TAG", decoded, value
        if decoded == "GPSInfo":
            gps_data = {}
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                gps_data[sub_decoded] = value[t]
            ret[decoded] = gps_data

            lat = None
            lon = None
            gps_latitude = _get_if_exist(gps_data, "GPSLatitude")
            gps_latitude_ref = _get_if_exist(gps_data, 'GPSLatitudeRef')
            gps_longitude = _get_if_exist(gps_data, 'GPSLongitude')
            gps_longitude_ref = _get_if_exist(gps_data, 'GPSLongitudeRef')
            
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = _convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":                     
                    lat = 0 - lat

                lon = _convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lon = 0 - lon
                    
            ret['latitude'] = lat
            ret['longitude'] = lon
            altitude = _get_if_exist(gps_data, 'GPSAltitude')
            if altitude:
                altitude = _fractToSimple(altitude)
            ret['altitude'] = altitude
            #print "altitude", ret['altitude']
        else:
            ret[decoded] = value
    try:
        iptc = IptcImagePlugin.getiptcinfo(i)
        ret['headline'] = iptc[(2,105)]
        ret['caption'] = iptc[(2,120)]
        ret['copyright'] = iptc[(2,116)]
        ret['keywords'] = iptc[(2,25)]
    except:
        ret['headline'] = None
        ret['caption'] = None
        ret['copyright'] = None
        ret['keywords'] = []

    return ret

def ExtractMakeAndModel(data):
    "Extracts make and model from data produced by pyexiv2."    
    make = data.get('Exif.Image.Make', None)
    model = data.get('Exif.Image.Model', None)
    if make and model:
        return make.value, model.value
    return None, None

def ExtractLocationData(data):
    try: location_name = ', '.join(data['Iptc.Application2.LocationName'].values)
    except: location_name = None
    try: city = ', '.join(data['Iptc.Application2.City'].values)
    except: city = None
    try: province_state = ', '.join(data['Iptc.Application2.ProvinceState'].values)
    except: province_state = None
    try: country_code = ', '.join(data['Iptc.Application2.CountryCode'].values)
    except: country_code = None
    try: country_name = ', '.join(data['Iptc.Application2.CountryName'].values)
    except KeyError: country_name = None
    return location_name, city, province_state, country_code, country_name

def ExtractGPSInfo(data):
    "Extracts longitude, latitude and altitude from data produced by pyexiv2."
    # http://linfiniti.com/2009/06/reading-geotagging-data-from-blackberry-camera-images/
    myLonDirection = None
    myLonDegrees = None
    myLonMinutes = None
    myLatDirection = None
    myLatDegrees = None
    myLatMinutes = None
    try:
        # Will be either 'E' or 'W'
        myLonDirection = data['Exif.GPSInfo.GPSLongitudeRef']
        # Will return a rational number like : '27/1'
        myLonDegrees = data['Exif.GPSInfo.GPSLongitude'][0]
        # Will return a rational number like : '53295/1000'
        myLonMinutes = data['Exif.GPSInfo.GPSLongitude'][1]
        # Will be either 'N' or 'S'
        myLatDirection = data['Exif.GPSInfo.GPSLatitudeRef']
        # Will return a rational number like : '27/1'
        myLatDegrees = data['Exif.GPSInfo.GPSLatitude'][0]
        # Will return a rational number like : '56101/1000'
        myLatMinutes = data['Exif.GPSInfo.GPSLatitude'][1]
    except:
        return (None, None, None)

    # Get the degree and minute values

    myRegexp = re.compile( '^[0-9]*' )
    myLonDegreesFloat = float(myRegexp.search( str(myLonDegrees) ).group())
    myLatDegreesFloat = float(myRegexp.search( str(myLatDegrees) ).group())
    myLonMinutesFloat = float(myRegexp.search( str(myLonMinutes) ).group())
    myLatMinutesFloat = float(myRegexp.search( str(myLatMinutes) ).group())

    # Divide the values by the divisor 

    myRegexp = re.compile( '[0-9]*$' )
    myLon = myLonDegreesFloat / float(myRegexp.search( str(myLonDegrees) ).group())
    myLat = myLatDegreesFloat / float(myRegexp.search( str(myLatDegrees) ).group())
    myLonMin = myLonMinutesFloat / float(myRegexp.search( str(myLonMinutes) ).group())
    myLatMin = myLatMinutesFloat / float(myRegexp.search( str(myLatMinutes) ).group())

    # We now have degrees and decimal minutes, so convert to decimal degrees...

    myLon = myLon + (myLonMin / 60)
    myLat = myLat + (myLatMin / 60)

    # Use a negative sign as needed

    if myLonDirection == 'W': myLon = 0 - myLon
    if myLatDirection == 'S': myLat = 0 - myLat

    try:
        altitude = data['Exif.GPSInfo.GPSAltitude'][0]
    except:
        altitude = None

    #print myLon, myLat, altitude
    return (myLon, myLat, altitude)

def exiv2ToDict(metadata):
    result = {}
    keys = metadata.exif_keys
    keys.extend(metadata.iptc_keys)
    keys.extend(metadata.xmp_keys)
    for key in keys:
        result[key] = metadata[key]
    return result

def prettyPrintexiv2(metadata):
    result = {}
    for k,v in metadata.items():
        if hasattr(v, 'values'):
            result[k] = ' '.join(v.values)
        else:
            result[k] = str(v.value)
    return result

def ExtractPhotoMetadata(filename):
    """
    """
    if not PYEXIV2_SUPPORT:
        return {}
    
    metadata = pyexiv2.ImageMetadata(filename)
    metadata.read()
    result = exiv2ToDict(metadata)
    result['width'], result['height'] = metadata.dimensions
    return result

metadata_fields = {
    'camera_model': None,
    'manufacturer': None,
    'orientation': None,
    'exposure_time': None,
    'fnumber': None,
    'exposure_program': None,
    'iso_speed': None,
    'metering_mode': None,
    'light_source': None,
    'flash_used': None,
    'focal_length': None,
    'longitude': None,
    'latitude': None,
    'altitude': None,
    'exposure_mode': None,
    'whitebalance': None,
    'focal_length_in_35mm': None,
    'width': None,
    'height': None,
    'keywords': None,
    'headline': None,
    'caption': None,
    'copyright': None,
    'software': None,
    }


def get_metadata(filename):
    result = metadata_fields.copy()
    try:
        metadata = get_exif(filename)
        #import pprint
        #pprint.pprint(metadata)
        #for k,v in metadata.items():
        #    print "TAG", k, v, str(v)
        # EXIF
        tm = time.strptime(metadata.get('DateTime', metadata.get('DateTimeOriginal', metadata.get('DateTimeDigitized'))),"%Y:%m:%d %H:%M:%S")
        result['exif_date'] = datetime.datetime.fromtimestamp(time.mktime(tm))
        result['camera_model'] = metadata.get("Model", None)
        result['orientation'] = metadata.get("Orientation", None)
        result['exposure_time'] = _fractToSimple(metadata.get("ExposureTime", metadata.get('ShutterSpeedValue', 0)))
        result['fnumber'] = _fractToSimple(metadata.get("FNumber", -1.0))
        result['exposure_program'] = metadata.get("ExposureProgram", None)
        result['iso_speed'] = metadata.get("ISOSpeedRatings", None)
        result['metering_mode'] = metadata.get("MeteringMode", None)
        result['light_source'] = metadata.get("LightSource", None)
        result['flash_used'] = metadata.get("Flash", None)
        result['focal_length'] = _fractToSimple(metadata.get("FocalLength", -1.0))
        result['width'] = metadata.get('ExifImageWidth', None)
        result['height'] = metadata.get('ExifImageHeight', None)
        result['software'] = metadata.get('Software')
        result['manufacturer'] = metadata.get('Make')

        # IPTC
        result['keywords'] = metadata.get('Keywords', None)
        result['headline'] = metadata.get('Headline', metadata.get('By-line'))
        result['caption'] = metadata.get('Caption', metadata.get('ImageDescription'))
        result['copyright'] = metadata.get('Copyright', None)
        # GPS tags
        result['longitude'] = metadata.get('longitude')
        result['latitude'] = metadata.get('latitude')
        result['altitude'] = metadata.get('altitude')

    except Exception, e:
        print "Error using PIL: %s for file %s." % (e, filename)
        if PYEXIV2_SUPPORT:
            try:
                metadata = ExtractPhotoMetadata(filename)
                # EXIF
                try:                    
                    result['exif_date'] = metadata['Exif.Image.DateTime'].value
                except:
                    result['exif_date'] = datetime.datetime.fromtimestamp(os.stat(filename).st_ctime)
                result['camera_model'] = metadata.get("Exif.Image.Model", None)
                result['orientation'] = metadata.get("Exif.Image.Orientation", None)
                if result['orientation']:
                    result['orientation'] = result['orientation'].value
                result['exposure_time'] = metadata.get("Exif.Photo.ExposureTime", None)
                result['fnumber'] = metadata.get("Exif.Photo.FNumber", None)
                result['exposure_program'] = metadata.get("Exif.Photo.ExposureProgram", None)
                result['iso_speed'] = metadata.get("Exif.Photo.ISOSpeedRatings", None)
                result['metering_mode'] = metadata.get("Exif.Photo.MeteringMode", None)
                result['light_source'] = metadata.get("Exif.Photo.LightSource", None)
                result['flash_used'] = metadata.get("Exif.Photo.Flash", None)
                result['focal_length'] = metadata.get("Exif.Photo.FocalLength", None)
                longitude, latitude, altitude = ExtractGPSInfo(metadata)
                result['longitude'] = longitude
                result['latitude'] = latitude
                result['altitude'] = altitude
                result['exposure_mode'] = metadata.get("Exif.Photo.ExposureMode", None)
                result['whitebalance'] = metadata.get("Exif.Photo.WhiteBalance", None)
                result['focal_length_in_35mm'] = metadata.get("Exif.Photo.FocalLengthIn35mmFilm", None)
                result['width'] = metadata.get('ExifImageWidth', None)
                result['height'] = metadata.get('ExifImageHeight', None)
                # IPTC
            except Exception, e:
                print "Error using PYEXIV: %s for file %s." % (e, filename)
    if not 'exif_date' in result:
        result['exif_date'] = datetime.datetime.fromtimestamp(os.stat(filename).st_ctime)
    return result
