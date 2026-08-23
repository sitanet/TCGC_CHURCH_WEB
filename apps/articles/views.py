"""
Views and API for articles.
"""
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer


class ArticleListApiView(generics.ListAPIView):
    queryset = Article.objects.filter(status="published")
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_featured"]
    search_fields = ["title", "summary", "body"]
    ordering_fields = ["published_at", "view_count"]


class ArticleDetailApiView(generics.RetrieveAPIView):
    queryset = Article.objects.filter(status="published")
    serializer_class = ArticleSerializer
    lookup_field = "slug"
