from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Primary IMGC Registration Routes
    path('imgc/', views.registration, name='registration'),
    path('imgc/confirmation/<str:registration_code>/', views.registration_confirmation, name='registration_confirmation'),

    # Redirects to /imgc/
    path('registration/', RedirectView.as_view(pattern_name='registration', permanent=True)),
    path('registration/confirmation/<str:registration_code>/', RedirectView.as_view(pattern_name='registration_confirmation', permanent=True)),
    path('imgc/register/', RedirectView.as_view(pattern_name='registration', permanent=True)),
    path('events/imgc/', RedirectView.as_view(pattern_name='registration', permanent=True)),
    # IMGC Personalized Invitation Routes
    path('imgc/invite/', views.fls_invite_view, name='imgc_invite'),
    path('imgc26/invite/', views.fls_invite_view, name='imgc26_invite'),
    path('invite/', views.fls_invite_view, name='invite'),
    path('imgc/invite/image/', views.fls_invite_image_api, name='imgc_invite_image'),
    path('imgc/invite/pdf/', views.fls_invite_pdf_api, name='imgc_invite_pdf'),
    path('imgc26/invite/image/', views.fls_invite_image_api, name='imgc26_invite_image'),
    path('imgc26/invite/pdf/', views.fls_invite_pdf_api, name='imgc26_invite_pdf'),

    # Testimonies & Praise Reports
    path('testimony/', views.testimony_view, name='testimony'),
    path('testimonies/', views.testimony_view, name='testimonies'),

    # Media & Pages
    path('watch-live/', views.video_streaming, name='video_streaming'),
    path('listen-live/', views.audio_streaming, name='audio_streaming'),
    path('ministries/', views.ministries, name='ministries'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/live-video/', views.api_live_video, name='api_live_video'),
]
