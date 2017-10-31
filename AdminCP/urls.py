from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^login$", views.login_acp, name="ACP-Login"),
    url(r'^$', views.index, name="ACP-index"),
    url(r'^access_log$', views.access_log_home, name="ACP-AccessLog"),
    url(r'^users/$', views.users_index, name="ACP-Users-index"),
    url(r'^users/create$', views.create_user, name="ACP-Users-Create"),
    url(r'^users/delete_profile/(?P<user_id>\d{1,3})$', views.delete_profile),
    url(r'^users/delete_profile', views.delete_profile, name="ACP-Users-DeleteProfile"),
    url(r'^users/delete/(?P<id_to_del>\d{1,3})$', views.delete_user),
    url(r'^users/delete', views.delete_user, name="ACP-Users-Delete"),
    url(r'^unlock$', views.acp_unlock, name="ACP-Unlock"),
]