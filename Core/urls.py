from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('find_skills/', views.find_skills, name='find_skills'),
    path('remove_skill/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    path('add_skill/', views.add_skill, name='add_skill'),
    path('edit-skill/<int:skill_id>/', views.edit_skill, name='edit_skill'),
    path('delete-skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path("send-swap-request/<int:skill_id>/", views.send_swap_request, name="send_swap_request"),
    path("swap-requests/", views.swap_requests, name="swap_requests"),
     path("accept-request/<int:request_id>/", views.accept_request, name="accept_request"),
    path("reject-request/<int:request_id>/", views.reject_request, name="reject_request"),
    path("cancel-request/<int:request_id>/", views.cancel_request, name="cancel_request"),
    path('accept-request/<int:request_id>/', views.accept_request, name="accept_request"),
    path('matching-swaps/', views.matching_swaps, name="matching_swaps"),
    path('about-us/', views.aboutus, name='aboutus'),
]