from django.urls import path
from . import views

urlpatterns = [
    path('', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/upload-pic/", views.upload_profile_pic, name="upload_profile_pic"),
    path("profile/delete-pic/", views.delete_profile_pic, name="delete_profile_pic"),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:reset_token>/', views.reset_password_view, name='reset_password'),
    path('contact/',views.contact, name='contact'),
    
]