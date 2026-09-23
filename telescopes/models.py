from django.db import models
from django.conf import settings


class Telescope(models.Model):
    STATUS_ONLINE = 'online'
    STATUS_SLEWING = 'slewing'
    STATUS_TRACKING = 'tracking'
    STATUS_IDLE = 'idle'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_FAULT = 'fault'

    STATUS_CHOICES = [
        (STATUS_ONLINE, 'Online / Ready'),
        (STATUS_SLEWING, 'Slewing Target'),
        (STATUS_TRACKING, 'Tracking Target'),
        (STATUS_IDLE, 'Parked / Standby'),
        (STATUS_MAINTENANCE, 'Maintenance Mode'),
        (STATUS_FAULT, 'System Fault'),
    ]

    MOUNT_CHOICES = [
        ('alt_az', 'Alt-Azimuth Mount'),
        ('german_eq', 'German Equatorial Mount'),
        ('fork_eq', 'Fork Equatorial Mount'),
    ]

    DOME_CHOICES = [
        ('closed', 'Closed'),
        ('open', 'Open'),
        ('parkov', 'Parked'),
        ('rotating', 'Rotating / Slewing'),
    ]

    name = models.CharField(max_length=150, help_text="Official name of the observatory telescope.")
    code = models.CharField(max_length=20, unique=True, help_text="Short system code identifier.")
    aperture = models.FloatField(help_text="Primary mirror aperture diameter in meters.")
    focal_ratio = models.CharField(max_length=10, default="f/9", help_text="Focal ratio (e.g., f/9, f/11).")
    mount_type = models.CharField(max_length=20, choices=MOUNT_CHOICES, default='alt_az')
    location = models.CharField(max_length=100, default="IIA Observatory Site")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IDLE)
    
    # Coordinates & Control Parameters
    right_ascension = models.CharField(max_length=30, default="00h 00m 00.0s")
    declination = models.CharField(max_length=30, default="+00° 00' 00.0\"")
    epoch = models.CharField(max_length=10, default="J2000")
    focus_position = models.FloatField(default=12.50, help_text="Focuser position in mm.")
    
    # Dome & Enclosure
    dome_status = models.CharField(max_length=20, choices=DOME_CHOICES, default='closed')
    dome_azimuth = models.FloatField(default=0.0, help_text="Dome azimuth angle in degrees.")
    primary_mirror_temp = models.FloatField(default=5.2, help_text="Mirror temperature in °C.")
    ambient_temp = models.FloatField(default=2.1, help_text="Ambient dome air temperature in °C.")
    humidity = models.FloatField(default=35.0, help_text="Relative humidity percentage.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telescope"
        verbose_name_plural = "Telescopes"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_status_display()})"


class TelescopeLog(models.Model):
    EVENT_CHOICES = [
        ('slew', 'Slew Execution'),
        ('track_start', 'Tracking Started'),
        ('track_stop', 'Tracking Stopped'),
        ('dome_open', 'Dome Opened'),
        ('dome_close', 'Dome Closed'),
        ('fault', 'Hardware Fault'),
        ('maintenance', 'Maintenance Action'),
    ]

    telescope = models.ForeignKey(Telescope, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default='slew')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telescope Log"
        verbose_name_plural = "Telescope Logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.telescope.code}: {self.get_event_type_display()}"


class TelescopeDiscussion(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General Observatory Chat'),
        ('observation', 'Observation Logs & Targets'),
        ('hardware', 'Hardware & Mount Operations'),
        ('optics', 'Optics & Focusing'),
        ('software', 'Software & Plate Solving'),
        ('maintenance', 'Maintenance Notes'),
    ]

    telescope = models.ForeignKey(Telescope, on_delete=models.CASCADE, related_name="discussions", help_text="Separate telescope for this discussion thread")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telescope_discussions")
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telescope Discussion"
        verbose_name_plural = "Telescope Discussions"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"[{self.telescope.code}] {self.title}"


class TelescopeDiscussionReply(models.Model):
    discussion = models.ForeignKey(TelescopeDiscussion, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telescope_discussion_replies")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telescope Discussion Reply"
        verbose_name_plural = "Telescope Discussion Replies"
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by @{self.user.username} on '{self.discussion.title}'"

