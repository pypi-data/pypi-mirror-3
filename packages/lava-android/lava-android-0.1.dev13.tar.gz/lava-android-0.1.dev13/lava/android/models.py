import logging

from django.db import models
from django.utils.translation import ugettext as _

from dashboard_app.models import TestRun, NamedAttribute
from dashboard_app.signals import bundle_was_deserialized


class AndroidBuild(models.Model):

    name = models.CharField(
        max_length=1000,
        verbose_name=_("Build name"))

    number = models.PositiveIntegerField(
        verbose_name=_("Build number"))

    url = models.CharField(
        verbose_name=_("Build URL"),
        max_length=1000)

    test_runs = models.ManyToManyField(
        TestRun,
        related_name="android_builds")

    class Meta:

        unique_together = (
            ('name', 'number'))


def scan_for_android_builds(bundle):
    """
    Scan (presumably just deserialized) bundle for android data and construct
    AndroidBuild objects.
    """
    builds = []
    for test_run in bundle.test_runs.all():
        # Find build number/name/url
        try:
            build_number = test_run.attributes.get(name='android.build').value
            build_name = test_run.attributes.get(name='android.name').value
            build_url = test_run.attributes.get(name='android.url').value
        except NamedAttribute.DoesNotExist:
            # Skip non-android test runs
            continue
        # Convert build number to integer
        try:
            build_number = int(build_number)
        except ValueError:
            # Skip malformed build numbers
            logging.warning("android.build in %r was not a number (%r)",
                            test_run, build_number)
            continue
        # Lookup corresponding AndroidBuild object
        android_build, created = AndroidBuild.objects.get_or_create(
            number=build_number, name=build_name)
        # Save if needed, we'll be changing m2m relations
        if created:
            # Store the URL if we're creating a new instance
            android_build.url = android_build.url
            android_build.save()
        # Add all monkey and 0xbench test runs to the list 
        if test_run.test.test_id in ("monkey", "0xbench"):
            android_build.test_runs.add(test_run)
        # Collect builds
        builds.append(android_build)
    return builds


# Detect android data in incoming bundles 
bundle_was_deserialized.connect(
    lambda sender, bundle, **kwargs: scan_for_android_builds(bundle))
