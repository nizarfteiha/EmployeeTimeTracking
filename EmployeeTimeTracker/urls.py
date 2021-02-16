from timetrackingapi import urls as timetrackingapi_urls
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(timetrackingapi_urls))
]
