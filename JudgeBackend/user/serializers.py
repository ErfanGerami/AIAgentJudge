from rest_framework import serializers
from .models import Submission, SubmissionTestCase,Problem
from django.contrib.auth import get_user_model


class SubmissionTestCaseSerializer(serializers.ModelSerializer):
    testcase_id = serializers.IntegerField(source="testcase.id", read_only=True)

    class Meta:
        model = SubmissionTestCase
        fields = ["testcase_id", "result"]

class SubmissionSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    file = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Submission
        fields = ["id", "user", "problem", "file", "time", "score"]
        read_only_fields = ["user", "score", "time"]

    def get_score(self, obj):
        return sum(stc.testcase.score for stc in obj.subtests.filter(result="AC"))



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user
    


class ProblemSerializer(serializers.ModelSerializer):
    max_score=serializers.SerializerMethodField()
    class Meta:
        model = Problem
        exclude = ['judge_file'] 
    def get_max_score(self, obj):
        return sum(stc.score for stc in obj.testcases.all())


class SubmissionDetailsSerilizer(serializers.ModelSerializer):
    TLE=serializers.SerializerMethodField()
    RE=serializers.SerializerMethodField()
    AC=serializers.SerializerMethodField()
    WR=serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['WR','TLE','AC','RE','time']
    def get_TLE(self, obj):
        return SubmissionTestCase.objects.filter(submission=obj).filter(result="TLE").count()
    def get_AC(self, obj):
        return SubmissionTestCase.objects.filter(submission=obj).filter(result="AC").count()
    def get_RE(self, obj):
        return SubmissionTestCase.objects.filter(submission=obj).filter(result="RE").count()
    def get_WR(self,obj):
        return SubmissionTestCase.objects.filter(submission=obj).filter(result="WR").count()

        