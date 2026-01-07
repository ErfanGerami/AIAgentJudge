import os
import shutil
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import redis
from django.conf import settings
import json
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)


def judge_file_upload_path(instance, filename):
    return f"problems/{instance.id}/judge.py"


def testcase_related_files_upload_path(instance, filename,format):
    return f"problems/{instance.problem.id}/testcases/{instance.id}.{format}"



def submission_upload_path(instance, filename):
    return f"submissions/{instance.user.username}/{instance.problem.id}/{instance.id}/main.py"

def move_file(file,new_path):
    current_path = file.path
    full_path = os.path.join(settings.MEDIA_ROOT, new_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if os.path.exists(full_path) and os.path.abspath(current_path) != os.path.abspath(full_path):
        os.remove(full_path)
    shutil.move(current_path, full_path)
    file.name = new_path


class MyUser(AbstractUser):
    def __str__(self):
        return self.username


class Problem(models.Model):
    file = models.FileField(upload_to="problem_files")
    judge_file = models.FileField(upload_to="temp/", blank=True, null=True)
    title = models.CharField(max_length=100)
    memory_limit = models.BigIntegerField(default=256000000)
    storage_limit = models.BigIntegerField(default=1000000000)
    time_limit = models.IntegerField(default=10)
    number=models.IntegerField(unique=True,default=1)

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)

        current_path = self.judge_file.path
        new_path = judge_file_upload_path(self, self.judge_file.name)
        move_file(self.judge_file,new_path)
        super().save(*args, **kwargs)

        return self
       

    def __str__(self):
        return self.title


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, related_name="testcases", on_delete=models.CASCADE)
    input_file = models.FileField(upload_to="temp/", blank=True, null=True)
    ans_file = models.FileField(upload_to="temp/", blank=True, null=True)
    file=models.FileField(blank=True,null=True,default=None,upload_to="temp/")
    score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.problem.save()
        super().save(*args, **kwargs)
        new_input_path = testcase_related_files_upload_path(self, self.file.name,"in")
        move_file(self.input_file,new_path=new_input_path)
        new_ans_path=testcase_related_files_upload_path(self, self.file.name,"ans")
        move_file(self.ans_file,new_path=new_ans_path)
        new_file_path=testcase_related_files_upload_path(self, self.file.name,self.file.name.split(".")[-1])
        move_file(self.file,new_path=new_file_path)
        super().save(*args, **kwargs)
        return self
    

    def __str__(self):
        return f"{self.problem}:{self.id}"


class Submission(models.Model):
    user = models.ForeignKey(MyUser, related_name="submissions", on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, related_name="submissions", on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="temp/", blank=True, null=True)
    status = models.CharField(default="pending", max_length=100)
    do_rejudge = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if(self.do_rejudge and self.pk):
            self.rejudge()
            self.do_rejudge=False
        super().save(*args, **kwargs)
        new_path = submission_upload_path(self, self.file.name)
        move_file(self.file,new_path)
        
        super().save(update_fields=['file'] if self.file else None)
        return self
    
    def rejudge(self):
        SubmissionTestCase.objects.filter(submission=self).delete()
        self.judge()

    def judge(self):
        data = {
            "username": self.user.username,
            "problem_id": self.problem.id,
            "submission_id": self.id,
            "testcases": json.dumps(
                list(self.problem.testcases.order_by("id").values_list("id", flat=True))
            ),
            "max_score": json.dumps(
                list(self.problem.testcases.order_by("id").values_list("score", flat=True))
            ),
            "files": json.dumps([
                os.path.basename(f) if f else None
                for f in self.problem.testcases.order_by("id").values_list("file", flat=True)
            ]),

            "memory_limit": self.problem.memory_limit,
            "time_limit": self.problem.time_limit,
            "storage_limit": self.problem.storage_limit,
        }

        msg_id = r.xadd(settings.STREAM_NAME, data)

    def __str__(self):
        return f"{self.status}:{self.user.username} ({self.problem.id},{self.id})"


class SubmissionTestCase(models.Model):
    submission = models.ForeignKey(Submission, related_name="subtests", on_delete=models.CASCADE)
    testcase = models.ForeignKey(TestCase, related_name="submissions", on_delete=models.CASCADE)
    result = models.CharField(max_length=10)
    score=models.IntegerField(default=0)

    def __str__(self):
        return f"{self.submission}: {self.result}"