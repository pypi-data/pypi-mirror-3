import time
from django.core.management.base import BaseCommand
from django.conf import settings
from hardworker.models import HardJob
import sys


class Command(BaseCommand):
    """

    """
    args = ''
    help = "Handle hard jobs."

    def handle(self, *args, **options):
        """

        """
        interval = hasattr(settings, 'HARDWORKER_INTERVAL') and settings.HARDWORKER_INTERVAL or 10
        print "HardWorking background worker is working hard every %s seconds." % interval
        HardJob.look_for_jobs()
        while 1:
            try:
                time.sleep(interval)
                if settings.DEBUG:
                    print "Looking for work ..."
                print HardJob.look_for_jobs()
            except KeyboardInterrupt:
                print "Hardworker daemon stopped."
                sys.exit(0)
