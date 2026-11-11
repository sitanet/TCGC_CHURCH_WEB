from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Primary IMGC Registration Routes
    path('imgc/', views.registration, name='registration'),
    path('imgc/confirmation/<str:registration_code>/', views.registration_confirmation, name='registration_confirmation'),
    path('imgc/edit/', views.registration_edit_lookup, name='registration_edit_lookup'),
    path('imgc/edit/<str:registration_code>/', views.registration_edit, name='registration_edit'),

    # Redirects & Aliases
    path('registration/', RedirectView.as_view(pattern_name='registration', permanent=True)),
    path('registration/confirmation/<str:registration_code>/', RedirectView.as_view(pattern_name='registration_confirmation', permanent=True)),
    path('registration/edit/', RedirectView.as_view(pattern_name='registration_edit_lookup', permanent=False)),
    path('registration/edit/<str:registration_code>/', RedirectView.as_view(pattern_name='registration_edit', permanent=False)),
    path('imgc/retrieve/', RedirectView.as_view(pattern_name='registration_edit_lookup', permanent=False)),
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

    # NEW: "I Will Be Attending" Video & Picture DP Maker Routes
    path('imgc/attending/', views.attending_dp_view, name='attending_dp'),
    path('imgc/attending', views.attending_dp_view, name='attending_dp_noslash'),
    path('attending/', views.attending_dp_view, name='attending_dp_short'),
    path('attending', views.attending_dp_view, name='attending_dp_short_noslash'),
    path('api/generate-attending-video/', views.api_generate_attending_video, name='api_generate_attending_video'),

    # Media & Pages
    path('watch-live/', views.video_streaming, name='video_streaming'),
    path('tcgc/watchlive_mobile/', views.video_streaming, name='watchlive_mobile'),
    path('watchlive_mobile/', views.video_streaming, name='watchlive_mobile_short'),
    path('stream/', views.video_streaming, name='stream_alias'),
    path('app/watch-live/', views.video_streaming, name='app_watch_live'),
    path('app/listen-live/', views.audio_streaming, name='app_listen_live'),
    path('listen-live/', views.audio_streaming, name='audio_streaming'),
    path('tcgc/listenlive_mobile/', views.audio_streaming, name='listenlive_mobile'),
    path('listenlive_mobile/', views.audio_streaming, name='listenlive_mobile_short'),
    path('radio/', views.audio_streaming, name='radio'),
    path('audio-stream/', views.audio_streaming, name='audio_stream'),
    path('api/live-audio/', views.api_live_audio, name='api_live_audio'),
    path('ministries/', views.ministries, name='ministries'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/live-video/', views.api_live_video, name='api_live_video'),
]
