from django.urls import path

from . import views

urlpatterns = [
    path('diyp/', views.diyp),
    path('web/', views.web_single_channel_epg),
    path('test/', views.d),
]
