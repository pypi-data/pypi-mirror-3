import hashlib
import sys
import os
import shutil
from datetime import datetime
import time
from metadata import get_metadata, get_exif


# Sort of constants ;-)

months = {}
if not months:
    for month in range(1,12+1):
        date = datetime(1900, month, 1)
        months[month] = date.strftime('%B')

norwegian_months = {
    1: 'Januar',
    2: 'Februar',
    3: 'Mars',
    4: 'April',
    5: 'Mai',
    6: 'Juni',
    7: 'Juli',
    8: 'August',
    9: 'September',
    10: 'Oktober',
    11: 'November',
    12: 'Desember'
}

photo_extensions_to_include = (
    'jpg',
    'nef',
    'png',
    'bmp',
    'gif',
    'cr2',
    'tif',
    'tiff',
    'jpeg',
    )


timestamp_format = '%Y%m%d_%H%M%S%f'
duplicate_filename_format = '%(filename)s~%(counter)s%(file_extension)s'
new_filename_format = "%(filename)s_%(timestamp)s%(file_extension)s"
ignore_files = ('thumbs.db', 'pspbrwse.jbf', 'picasa.ini', 'autorun.inf', 'hpothb07.dat',)
#FOLDERS_TO_SKIP = ('DCIM','100_FUJI'.'100CASIO',)


def get_date_from_file(filename):
    try:
        return get_metadata(filename).get('exif_date')
    except Exception, e:
        return datetime.fromtimestamp(os.stat(filename).st_ctime)


def generate_filename_from_date(filename, date=None):
    if not date:
        date = get_date_from_file(filename)

    filename = os.path.basename(filename)
    timestamp = date.strftime(timestamp_format)
    if timestamp in filename:
        filename = filename.replace(timestamp, '')

    fname, ext = os.path.splitext(filename)
    return new_filename_format % dict(filename=fname, timestamp=timestamp, file_extension=ext)


def generate_folders_from_date(date, tag=None):
    if not tag:
        tag = str(date.day)
    return os.sep.join([str(date.year), months[date.month], tag])


def dirwalk(dir, extensions_to_include = None):
    extensions_check = extensions_to_include != None
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath, extensions_to_include):
                ext = os.path.splitext(x)[-1][1:].lower()
                if extensions_check == False or ext in extensions_to_include:
                    yield x
        else:
            ext = os.path.splitext(fullpath)[-1][1:].lower()
            if extensions_check == False or ext in extensions_to_include:
                yield fullpath


def get_files_in_folder(folder, extensions_to_include=None):
    result = {}
    for filename in dirwalk(folder, extensions_to_include):
        path, filename = os.path.split(filename)
        result.setdefault(path, []).append(filename)
    return result


def get_photos_in_folder(folder):
    return get_files_in_folder(folder, extensions_to_include=photo_extensions_to_include)


def get_tag_from_filename(filename, source_dir):
    result = os.path.split(filename)[0][len(source_dir):]

    if result and result[0] == os.sep:
        result = result[1:]
        
    return result


def relocate_photos(source_dir, target_dir=None, append_timestamp=True, remove_source=True, tag=None):
    if not target_dir:
        target_dir = source_dir

    photos = get_files_in_folder(source_dir, photo_extensions_to_include)
    for path, filenames in photos.items():
        current_tag = tag
        for filename in filenames:
            complete_filename = os.path.join(path, filename)
            if not current_tag:
                current_tag = get_tag_from_filename(complete_filename, source_dir)
            relocate_photo(complete_filename, target_dir=target_dir, append_timestamp=append_timestamp, remove_source=remove_source, tag=current_tag)

    if remove_source:
        remove_source_folders(photos.keys())

def generate_valid_target(filename):
    counter = 1
    while 1:
        if not os.path.exists(filename):
            break
        fname, ext = os.path.splitext(filename)
        filename = duplicate_filename_format % dict(filename=fname, counter=counter, file_extension=ext)
        counter += 1
    return filename

def relocate_photo(filename, target_dir, date=None, append_timestamp=True, remove_source=True, tag=None, skip_existing=False, path_prefix=None):
    if not date:
        date = get_date_from_file(filename)

    if path_prefix:
        target_dir = os.path.join(target_dir, path_prefix, generate_folders_from_date(date, tag))
    else:
        target_dir = os.path.join(target_dir, generate_folders_from_date(date, tag))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    new_filename = os.path.join(target_dir, append_timestamp and generate_filename_from_date(filename, date) or os.path.basename(filename))

    if skip_existing and os.path.exists(new_filename):
        return

    new_filename = generate_valid_target(new_filename)

    if remove_source:
        shutil.move(filename, new_filename)
    else:
        shutil.copy(filename, new_filename)

    return new_filename


def remove_source_folders(folders):    
    for folder in folders:
        if len(list(dirwalk(folder))) == 0:
            os.removedirs(folder)

def find_duplicates(source_folder, target_folder, delete_duplicates=False, verbose=False):
    source_files = {}
    target_files = {}
    if verbose: print "Scanning source folder ...",
    for filename in dirwalk(source_folder):
        st = os.stat(filename)
        source_files.setdefault(st.st_size, []).append((filename, st))
    if verbose: print "done!"

    if verbose:print "Scanning target folder ...",
    for filename in dirwalk(target_folder):
        st = os.stat(filename)
        target_files.setdefault(st.st_size, []).append((filename, st))
    if verbose: print "done!"

    if verbose: print "Locating duplicates:"
    for filesize, filedata in target_files.items():
        existing_files = source_files.get(filesize, [])
        for existing_filename, existing_st in existing_files:
            for filename, st in filedata:
                existing_ctime = st.st_mtime < st.st_ctime and st.st_mtime or st.st_ctime
                st_ctime = existing_st.st_mtime < existing_st.st_ctime and existing_st.st_mtime or existing_st.st_ctime
                if existing_ctime == st_ctime:
                    if delete_duplicates:
                        os.remove(filename)
                    if verbose: print "%s appears to be a duplicate of %s." % (filename, existing_filename)
                    yield filename


def get_checksum(filename):
    fname, ext = os.path.splitext(filename)
    if ext:
        if ext[1:].lower() in photo_extensions_to_include:
            try:
                exif = get_exif(filename)
                return str(time.strptime(exif.get('DateTime', exif.get('DateTimeOriginal', exif.get('DateTimeDigitized'))),"%Y:%m:%d %H:%M:%S"))
            except Exception, e:
                print "Error using PIL on %s: %s." % (filename, e)

    f = open(filename)
    result = hashlib.sha512()
    while 1:
        data = f.read(4096)
        if not data:
            break
        result.update(data)
    return result.hexdigest()

def build_file_cache(path):
    result = {}
    for filename in dirwalk(path):
        p,f = os.path.split(filename)
        if f.lower() in ignore_files:
            continue
        st = os.stat(filename)
        result.setdefault(st.st_size, []).append(filename)
    return result

def find_new_files(source_folder, target_folder, verbose=False):
    if verbose: print "Scanning source folder ...",
    source_files = build_file_cache(source_folder)
    if verbose: print "done!"

    if verbose:print "Scanning target folder ...",
    target_files = build_file_cache(target_folder)
    if verbose: print "done!"

    sha_cache = {}
    if verbose: print "Locating new content:"
    for filesize, filenames in target_files.items():
        if not filesize in source_files.keys():
            for filename in filenames:
                if verbose: print filename
                yield filename
        else:
            for existing_filename in source_files[filesize]:
                for filename in filenames:

                    if existing_filename[:8] == filename[:8]:
                        continue

                    if not existing_filename in sha_cache:
                        sha_cache[existing_filename] = get_checksum(existing_filename)

                    if not filename in sha_cache:
                        sha_cache[filename] = get_checksum(filename)

                    if sha_cache[existing_filename] != sha_cache[filename]:
                        if verbose: print filename
                        yield filename

def print_tag(sourcefolder):
    for filename in dirwalk(sourcefolder):
        print filename, get_tag_from_filename(filename, sourcefolder)


def clean_up(sourcefolder):
    print "Cleaning up %s" % sourcefolder
    for filename in dirwalk(sourcefolder):
        if os.path.basename(filename) in ignore_files:
            os.remove(filename)

    paths = {}
    for path in [os.path.join(sourcefolder, path) for path in os.listdir(sourcefolder)]:

        if os.path.isdir(path):
            paths[os.path.join(sourcefolder, path)] = []
            
    for filename in dirwalk(sourcefolder):
        path, filename = os.path.split(filename)
        paths.setdefault(path, []).append(filename)

    path_names = paths.keys()
    path_names.sort()
    path_names.reverse()
    print path_names
    for path in path_names:
        if not paths[path]:
            try:
                os.removedirs(path)
            except Exception, e:
                print "Error removing %s because %s." % (path, e)


movie_extensions_to_include = ('avi', 'mov', 'mp4', 'mpg', 'mts', 'mpeg', 'mkv', '3gp', 'wmv', 'm2t',)


def relocate_movies(source_dir, target_dir=None, append_timestamp=True, remove_source=True, tag=None):
    if not target_dir:
        target_dir = source_dir

    movies = get_files_in_folder(source_dir, movie_extensions_to_include)
    for path, filenames in movies.items():
        current_tag = tag
        for filename in filenames:
            complete_filename = os.path.join(path, filename)
            if not current_tag:
                current_tag = get_tag_from_filename(complete_filename, source_dir)
            relocate_movie(complete_filename, target_dir=target_dir, append_timestamp=append_timestamp, remove_source=remove_source, tag=current_tag)

    if remove_source:
        remove_source_folders(movies.keys())


def relocate_movie(filename, target_dir, append_timestamp=True, remove_source=True, tag=None, skip_existing=False, path_prefix=None):
    st = os.stat(filename)
    date = st.st_ctime < st.st_mtime and datetime.fromtimestamp(st.st_ctime) or datetime.fromtimestamp(st.st_mtime)

    if path_prefix:
        target_dir = os.path.join(target_dir, path_prefix, generate_folders_from_date(date, tag))
    else:
        target_dir = os.path.join(target_dir, generate_folders_from_date(date, tag))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    new_filename = os.path.join(target_dir, append_timestamp and generate_filename_from_date(filename, date) or os.path.basename(filename))
    new_filename = generate_valid_target(new_filename)

    if skip_existing and os.path.exists(new_filename):
        return

    if remove_source:
        shutil.move(filename, new_filename)
    else:
        shutil.copy(filename, new_filename)

    return new_filename

def get_resolution_from_user_agent(request):
    screen_height, screen_width = None, None
    return screen_height, screen_width

def get_resolution_from_request(request):
    # http://johannburkard.de/blog/www/mobile/mobile-phone-pda-web-browser-screen-size-detection.html
    pass

usage = """
        Usage : python %s <option> <source-folder> <target-folder>

        Options:
            s  = restructure photos by EXIF-date
            m  = restructure movies by creation-date
            n  = print files not in source-folder compared to target-folder
            d  = locate duplicates in target-folder compared to source-folder
            dm = remove duplicates in target-folder compared to source-folder

        Examples:
            python %s s /home/thomas/tmp /home/thomas/Pictures/by_date

            """ % (sys.argv[0], sys.argv[0])

if __name__ == '__main__':
    #import pdb
    #pdb.set_trace()
    try:
        option = sys.argv[1]
        source, target = map(os.path.abspath, sys.argv[2:])
        if option == 'm':
            relocate_movies(source, target)
        elif option == 'n':
            list(find_new_files(source, target, verbose=True))
        elif option == 's':
            relocate_photos(source, target)
        elif option == "n":
            find_new_files(source, target, verbose=True)
        elif option == "d":
            find_duplicates(source, target, verbose=True)
        elif option == "dm":
            find_duplicates(source, target, delete_duplicates=True, verbose=True)
        elif option == "t":
            print_tag(source)
        else:
            print usage
    except Exception, e:
        print "Exception raised: %s." % e
        print usage
        sys.exit(1)
