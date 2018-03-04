from django.urls import path

from . import views

urlpatterns = [
    path(r"login", views.login_acp, name="ACP-Login"),
    path('', views.index, name="ACP-index"),
    path('access_log', views.access_log_home, name="ACP-AccessLog"),
    path('users/', views.users_index, name="ACP-Users-index"),
    path('users/create', views.create_user, name="ACP-Users-Create"),
    path('users/delete_profile/<int:user_id>', views.delete_profile),
    path('users/delete_profile', views.delete_profile, name="ACP-Users-DeleteProfile"),
    path('users/delete/<int:id_to_del>', views.delete_user),
    path('users/delete', views.delete_user, name="ACP-Users-Delete"),
    path('unlock', views.acp_unlock, name="ACP-Unlock"),
]