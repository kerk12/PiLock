from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^login$", views.login_acp, name="ACP-Login"),
    url(r'^$', views.index, name="ACP-index"),
    url(r'^access_log$', views.access_log_home, name="ACP-AccessLog")
]