# urls.py
from rest_framework.routers import DefaultRouter
from .views import SubmissionViewSet
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
router = DefaultRouter()
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = router.urls

urlpatterns = [
        path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

        path("register/", RegisterView.as_view(), name="register"),
        path('problems/',Problems.as_view()),
        path('mysubmissions/',MySubmissionsAPIView.as_view()),
        path("submission/<int:id>/",SubmissionDetails.as_view()),
        path("", include(router.urls)),         
]