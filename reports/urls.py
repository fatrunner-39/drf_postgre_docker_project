from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import VisibilityViewSet, ReportViewSet, ImageView, RetrieveDestroyImageView, CoachReportsView


router = DefaultRouter()

router.register('report/visible', VisibilityViewSet)
router.register('reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('report/images/', ImageView.as_view()),
    path('loader/images/<int:pk>/', RetrieveDestroyImageView.as_view()),
    path('coach/reports/', CoachReportsView.as_view()),
]
