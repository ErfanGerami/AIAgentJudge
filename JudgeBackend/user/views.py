from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import *
from .serializers import SubmissionSerializer,RegisterSerializer,ProblemSerializer,SubmissionDetailsSerilizer
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
import redis
from django.db.models.functions import Coalesce
from django.db.models import Sum, F, IntegerField, Q
from django.conf import settings
import json
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import  status
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
from JudgeBackend.permissions import IsInContest
from rest_framework import views
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
class Problems(generics.ListAPIView):
    queryset = Problem.objects.all().order_by('number')
    serializer_class = ProblemSerializer
    # permission_classes = [IsAuthenticated,IsInContest] 



class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all().select_related("user", "problem")
    serializer_class = SubmissionSerializer
    http_method_names = ["get", "post"]  
    permission_classes=[IsAuthenticated]
    def perform_create(self, serializer):
        user = self.request.user
        problem = serializer.validated_data["problem"]

        last_submission = (
            Submission.objects
            .filter(user=user, problem=problem)
            .order_by("-time")
            .first()
        )

        if last_submission:
            time_diff = timezone.now() - last_submission.time
            if time_diff < timedelta(seconds=60):
                remaining = 60 - int(time_diff.total_seconds())
                raise ValidationError(
                    f"Please wait {remaining} seconds before submitting again."
                )

        submission = serializer.save(user=user)
        submission.judge()


        
   
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

        data = {
            "user": serializer.data,
            "tokens": tokens
        }

        return Response(data, status=status.HTTP_201_CREATED)
    
class MySubmissionsAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        submissions = (
            Submission.objects
            .filter(user=user)
            .annotate(
                total_score=Coalesce(
                    Sum(
                        'subtests__score',
                        filter=Q(subtests__result='AC'),
                        output_field=IntegerField()
                    ),
                    0
                )
            )
            .select_related("problem")
            .distinct()
            .order_by("-time")
        )

        resp = []

        for sub in submissions:
            resp.append({
                "submission_id": sub.id,
                "problem_id": sub.problem.id,
                "problem_title": sub.problem.title,
                "submission_time": sub.time,
                "score": sub.total_score,
                "status": sub.status,
                "fully_accepted": not SubmissionTestCase.objects
                    .filter(submission=sub)
                    .exclude(result="AC")
                    .exists()
            })

        return Response(resp)




class SubmissionDetails(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailsSerilizer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    