from django.urls import path

from . import views

urlpatterns = [
    path("login", views.loginView, name="Login"),
    path("authentication", views.authenticateView, name="Authentication"),
    path('changepin', views.changePin, name="ChangePin"),
    path('weartoken', views.getWearToken, name="WearToken"),
    path(r'', views.index)
]