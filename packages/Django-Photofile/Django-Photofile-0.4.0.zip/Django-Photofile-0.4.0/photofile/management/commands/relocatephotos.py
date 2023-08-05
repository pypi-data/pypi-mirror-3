import os
import sys
from django.core.management.base import BaseCommand, CommandError

from photfile.utils import relocate_photos

usage = "Usage: python manage.py relocatephotos source target"

class Command(BaseCommand):
    args = '<source> <target>'
    help = "Relocate photos into folder structure based on EXIF-date."

    def handle(self, *args, **options):
        if len(args) != 2:
            print usage
            sys.exit(0)

        source, target = args
        if not os.path.isdir(source) or (target and not os.path.isdir(target)):
            print usage
            sys.exit(0)
    
        relocate_photos(source, target)
