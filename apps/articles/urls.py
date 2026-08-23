"""
URL patterns for articles.
"""
from django.urls import path
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.ArticleListApiView.as_view(), name="article_list"),
    path("<slug:slug>/", views.ArticleDetailApiView.as_view(), name="article_detail"),
]
