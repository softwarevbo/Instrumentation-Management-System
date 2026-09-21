from django.contrib import admin
from .models import ObservationTarget, ExposureRunLog


@admin.register(ObservationTarget)
class ObservationTargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'catalog_id', 'object_class', 'right_ascension', 'declination', 'magnitude', 'observation_date', 'recommended_filter')
    list_filter = ('object_class', 'recommended_filter')
    search_fields = ('name', 'catalog_id')


@admin.register(ExposureRunLog)
class ExposureRunLogAdmin(admin.ModelAdmin):
    list_display = ('target', 'signal_to_noise', 'seeing_arcsec', 'sky_transparency', 'started_at')
