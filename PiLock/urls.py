from django.conf.urls import url, include
from django.db.utils import OperationalError
"""PiLock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from AdminCP.notifications import check_for_debug_mode

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('main.urls')),
    url(r'^AdminCP/', include('AdminCP.urls')),
]

# Run the debug mode check once at startup.
try:
    check_for_debug_mode()
except OperationalError:  # Used when the DB hasn't been initialized yet. This prevents migration errors when there is no db created yet.
    pass
