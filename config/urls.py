from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('telescopes/', include('telescopes.urls', namespace='telescopes')),
    path('instruments/', include('instruments.urls', namespace='instruments')),
    path('observations/', include('observations.urls', namespace='observations')),
    path('maintenance/', include('maintenance.urls', namespace='maintenance')),
    path('platesolver/', include('platesolver.urls', namespace='platesolver')),
    path('', include('core.urls', namespace='core')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
