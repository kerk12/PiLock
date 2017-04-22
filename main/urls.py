from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^login$", views.loginView, name="Login"),
    url(r"^authentication", views.authenticateView, name="Authentication"),
    url(r'^changepin', views.changePin, name="ChangePin"),
    url(r'^$', views.index)
]