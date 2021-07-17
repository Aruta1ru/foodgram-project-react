from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', views.subscribe),
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
]
