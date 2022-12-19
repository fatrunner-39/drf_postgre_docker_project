from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, RoleViewSet, CoachToRunnerViewSet, CreateUserView, SubscribeViewSet

router = DefaultRouter()
router.register('registration', CreateUserView)
router.register('users', UserViewSet)
router.register('subscribes/user', SubscribeViewSet)
router.register('roles', RoleViewSet)
router.register('groups', CoachToRunnerViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
