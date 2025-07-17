from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from datetime import date
from .models import UserProfile

class AccessPeriodBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            try:
                user_profile = user.userprofile
                today = date.today()

                if user_profile.access_start_date and user_profile.access_start_date > today:
                    return None  # Access period has not started yet

                if user_profile.access_end_date and user_profile.access_end_date < today:
                    return None  # Access period has expired

                return user
            except UserProfile.DoesNotExist:
                # If no UserProfile exists, assume no access restrictions
                return user
        return None
