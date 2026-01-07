from django.contrib import admin
from .models import MyUser, Problem, TestCase, Submission, SubmissionTestCase


class TestCaseInline(admin.TabularInline):  # or use StackedInline if you want big fields
    model = TestCase
    extra = 1   # number of empty rows to display for new testcases
    fields = ("input_file", "ans_file","file","score")  # show only these fields in inline


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    inlines = [TestCaseInline]


@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_staff", "is_superuser")
    search_fields = ("username", "email")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "problem", "time")
    list_filter = ("problem", "time", "user")
    search_fields = ("user__username", "problem__title")


@admin.register(SubmissionTestCase)
class SubmissionTestCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "submission", "testcase", "result")
    list_filter = ("result",)
