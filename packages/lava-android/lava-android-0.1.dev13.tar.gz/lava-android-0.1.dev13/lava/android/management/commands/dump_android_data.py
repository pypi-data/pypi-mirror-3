from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from lava.android.models import AndroidBuild 


class Command(BaseCommand):

    help = _('Dump android build data (special case command)')

    def handle(self, *args, **options):
        builds = (AndroidBuild.objects
            .filter(name='linaro-android_staging-panda')
            .order_by('name', 'number'))
        for build in builds:
            self.stdout.write(
                _("Build {build.number} ({build.name}):\n")
                .format(build=build))
            test_runs = (
                build
                .test_runs
                .all()
                .order_by('test__test_id'))
            for test_run in test_runs:
                self.stdout.write(
                    _("\tTest {test_run.test} from run {test_run.analyzer_assigned_uuid}\n")
                    .format(test_run=test_run))
                test_results = (
                    test_run
                    .test_results
                    .all()
                    .order_by('relative_index'))
                for test_result in test_results:
                    self.stdout.write(
                        _("\t\tData {test_result.test_case}: {test_result.measurement}\n")
                        .format(test_result=test_result))
