from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileLoaderViewSet


router = DefaultRouter()

router.register('tracks', FileLoaderViewSet)

urlpatterns = [
    path('loader/', include(router.urls)),
]
