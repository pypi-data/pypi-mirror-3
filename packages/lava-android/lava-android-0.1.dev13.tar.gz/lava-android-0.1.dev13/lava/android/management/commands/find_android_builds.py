from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from dashboard_app.models import Bundle

from lava.android.models import scan_for_android_builds

class Command(BaseCommand):

    args = _('<bundle_stream_pathname bundle_stream_pathname..>')
    help = _('Scan specified pathname for android builds')

    def handle(self, *args, **options):
        if args:
            bundles = Bundle.objects.filter(bundle_stream__pathname__in=args)
        else:
            bundles = Bundle.objects.all()
        for bundle in bundles: 
            self.stdout.write(_("Scanning bundle: %s\n") % bundle)
            builds = scan_for_android_builds(bundle)
            if builds:
                cnt = len(builds)
                self.stdout.write(
                    ungettext(cnt, "Found %d build\n", "Found %d builds\n") % cnt)
