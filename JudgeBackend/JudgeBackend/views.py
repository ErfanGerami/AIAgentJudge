from rest_framework import views
import json
from django.conf import settings
from rest_framework.response import Response
from rest_framework.status import *
from django.db.models import Sum, F, IntegerField,Q
from django.db.models.functions import Cast, Coalesce
from user.models import SubmissionTestCase,Submission,TestCase
import logging
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from user.models import *
from django.conf import settings
import logging
from .permissions import IsInContest
class Return(views.APIView):
    def post(self,request):
        data=json.loads(request.body)
        logging.info(data)
        if("api-key" not in data or settings.API_KEY != data.get("api-key")):
            return Response(data={"error":"api-key not valid"},status=HTTP_401_UNAUTHORIZED)
        

        submission_id=data.get("submission_id")
        submission=Submission.objects.get(id=submission_id)
        result=data.get("result")

        for _testcase  in result:
            testcase=TestCase.objects.get(id=_testcase)
            SubmissionTestCase.objects.create(submission=submission,testcase=testcase,result=result[_testcase]["result"],score=result[_testcase]["score"])
            
        submission.status="done"
        submission.save()
        return Response({"message":"noted!"})

from django.db.models import Sum, Q, IntegerField
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import views

class Scoreboard(views.APIView):
    permission_classes = []

    def get(self, request):
        users = get_user_model().objects.all()
        problems = (
            Problem.objects
            .all()
            .order_by("id")
            .prefetch_related("testcases")
        )

        resp = []
        cutoff_time = datetime(2026, 1, 1, 10, 4, 4)

        for user in users:
            res = []
            time_sum = 0
            total_score = 0

            for problem in problems:
                submissions = (
                    Submission.objects
                    .filter(user=user, problem=problem )
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
                )

                best = submissions.order_by('-total_score', 'time').first()

                if best and best.total_score > 0:
                    score = best.total_score
                    time_sum += (best.time - settings.START_TIME).total_seconds()
                else:
                    score = 0

                total_score += score

                res.append({
                    "problem_id": problem.id,
                    "problem_title": problem.title,
                    "score": score,
                    "max_score": sum(tc.score for tc in problem.testcases.all())
                })
                # print(res)

            resp.append({
                "username": user.username,
                "result": res,
                "total_score": total_score,
                "time": time_sum
            })

        resp.sort(key=lambda x: (-x["total_score"], x["time"]))
        return Response(resp)
