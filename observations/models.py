from django.db import models
from django.conf import settings
from telescopes.models import Telescope
from instruments.models import Instrument


class ObservationTarget(models.Model):
    OBJECT_CHOICES = [
        ('galaxy', 'Galaxy'),
        ('nebula', 'Nebula / HII Region'),
        ('star', 'Star / Star Cluster'),
        ('exoplanet', 'Exoplanet Host'),
        ('solar_system', 'Solar System Object'),
        ('quasar', 'Quasar / AGN'),
        ('other', 'Other / Unknown'),
    ]

    name = models.CharField(max_length=150)
    catalog_id = models.CharField(max_length=50, blank=True, help_text="Catalog identifier (e.g. NGC 224, HD 209458).")
    right_ascension = models.CharField(max_length=30, blank=True, default="00h 00m 00.0s", help_text="RA in HHh MMm SS.Ss format.")
    declination = models.CharField(max_length=30, blank=True, default="+00° 00' 00.0\"", help_text="DEC in ±DD° MM' SS.S\" format.")
    object_class = models.CharField(max_length=20, choices=OBJECT_CHOICES, default='star')
    magnitude = models.FloatField(null=True, blank=True, help_text="Visual magnitude.")
    distance_ly = models.FloatField(null=True, blank=True, help_text="Estimated distance in light-years.")
    observation_date = models.DateField(null=True, blank=True, help_text="Observation / entry date.")
    recommended_filter = models.CharField(max_length=50, default="V (550nm)", help_text="Filter used / recommended.")
    epoch = models.CharField(max_length=20, default="J2000.0", help_text="Astronomical coordinate epoch.")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Observation Target"
        verbose_name_plural = "Observation Targets"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.catalog_id or self.get_object_class_display()})"


class ExposureRunLog(models.Model):
    SKY_CHOICES = [
        ('photometric', 'Photometric'),
        ('clear', 'Clear'),
        ('thin_cloud', 'Thin Clouds'),
        ('variable', 'Variable'),
    ]

    target = models.ForeignKey(ObservationTarget, on_delete=models.CASCADE, related_name="runs", null=True, blank=True)
    fits_file_ref = models.CharField(max_length=200, blank=True, help_text="FITS file path or archive reference.")
    signal_to_noise = models.FloatField(null=True, blank=True, help_text="Achieved SNR.")
    seeing_arcsec = models.FloatField(null=True, blank=True, help_text="Measured atmospheric seeing in arcseconds.")
    sky_transparency = models.CharField(max_length=20, choices=SKY_CHOICES, default='clear')
    airmass = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Exposure Run Log"
        verbose_name_plural = "Exposure Run Logs"
        ordering = ['-started_at']

    def __str__(self):
        return f"Run: {self.target.name if self.target else 'Exposure'} | SNR={self.signal_to_noise}"
