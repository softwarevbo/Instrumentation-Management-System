from django.db import models
from django.conf import settings
from telescopes.models import Telescope


class PlateSolveRun(models.Model):
    STATUS_IDLE = 'idle'
    STATUS_SOLVING = 'solving'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_IDLE, 'Idle'),
        (STATUS_SOLVING, 'Solving in Progress'),
        (STATUS_SUCCESS, 'Solved Successfully'),
        (STATUS_FAILED, 'Solving Failed'),
    ]

    telescope = models.ForeignKey(Telescope, on_delete=models.SET_NULL, null=True, blank=True, related_name="plate_solves")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Input field center
    target_ra_deg = models.FloatField(default=0.0)
    target_dec_deg = models.FloatField(default=0.0)
    fov_deg = models.FloatField(default=20.0)
    
    # Solved WCS Solution
    solved_ra_deg = models.FloatField(null=True, blank=True)
    solved_dec_deg = models.FloatField(null=True, blank=True)
    pixel_scale_arcsec = models.FloatField(default=35.15)
    rotation_angle_deg = models.FloatField(default=0.0)
    matched_stars_count = models.IntegerField(default=0)
    solution_time_sec = models.FloatField(default=0.42)
    ra_error_arcmin = models.FloatField(default=0.0)
    dec_error_arcmin = models.FloatField(default=0.0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plate Solve Run"
        verbose_name_plural = "Plate Solve Runs"
        ordering = ['-created_at']

    def __str__(self):
        return f"Plate Solve #{self.pk} - {self.get_status_display()} (RA: {self.target_ra_deg:.3f}°, Dec: {self.target_dec_deg:.3f}°)"
