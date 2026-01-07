from rest_framework import permissions
from django.conf import settings
from django.utils.timezone import now

class IsInContest(permissions.BasePermission):
  
    message = "the contest is not running."

    def has_permission(self, request, view):
        current_time = now()
        # START_TIME should be a timezone-aware datetime
        start_time = getattr(settings, "START_TIME", None)
        if not start_time:
            return False  
        end_time = getattr(settings, "END_TIME", None)
        if not end_time:
            return True 

        return current_time >= start_time and current_time<=end_time
