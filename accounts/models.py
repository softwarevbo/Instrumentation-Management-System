from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model supporting multi-role access control:
    - Admin (Observatory / System Manager)
    - Engineer (Instrument / Maintenance Engineer)
    - Observer (Astronomer / Researcher)
    """
    ROLE_ADMIN = 'admin'
    ROLE_ENGINEER = 'engineer'
    ROLE_OBSERVER = 'observer'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Observatory Admin'),
        (ROLE_ENGINEER, 'Instrument Engineer'),
        (ROLE_OBSERVER, 'Astronomical Observer'),
    ]

    DEPARTMENT_CHOICES = [
        ('optics', 'Optics & Instrumentation'),
        ('electronics', 'Control Electronics'),
        ('software', 'Software & Telemetry'),
        ('astronomy', 'Observational Astronomy'),
        ('operations', 'Site Operations'),
    ]

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default=ROLE_OBSERVER,
        help_text="Primary functional role in the observatory system."
    )
    department = models.CharField(
        max_length=30, choices=DEPARTMENT_CHOICES, default='astronomy'
    )
    designation = models.CharField(max_length=100, blank=True, help_text="Job title or academic rank.")
    phone = models.CharField(max_length=20, blank=True)
    avatar_color = models.CharField(max_length=7, default="#4f8ef7")
    theme_preference = models.CharField(
        max_length=10,
        choices=[('dark', 'Dark Observatory Theme'), ('light', 'Light Theme')],
        default='dark'
    )

    assigned_telescopes = models.ManyToManyField(
        'telescopes.Telescope',
        blank=True,
        related_name='assigned_observers',
        help_text="Telescopes this observer is authorized to view and control."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_engineer(self):
        return self.role == self.ROLE_ENGINEER or self.is_admin

    @property
    def is_observer(self):
        return self.role == self.ROLE_OBSERVER or self.is_admin

    def can_access_telescope(self, telescope):
        """Engineers and Admins can access ALL telescopes; Observers can ONLY access assigned telescopes."""
        if self.is_admin or self.is_engineer:
            return True
        if self.role == self.ROLE_OBSERVER:
            return self.assigned_telescopes.filter(pk=telescope.pk).exists()
        return False

    def get_accessible_telescopes(self):
        """Returns QuerySet of telescopes accessible by this user."""
        from telescopes.models import Telescope
        if self.is_admin or self.is_engineer:
            return Telescope.objects.all()
        if self.role == self.ROLE_OBSERVER:
            return self.assigned_telescopes.all()
        return Telescope.objects.none()

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        name = self.get_full_name()
        if name:
            parts = name.split()
            return "".join(p[0].upper() for p in parts[:2])
        return self.username[:2].upper()
