from django.db import models
from django.contrib.auth.models import User
from datetime import date

class NationalRegister(models.Model):
    year = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    surname = models.CharField(max_length=255, null=True, blank=True)
    nrn = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    address_line_3 = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    postcode = models.CharField(max_length=255, null=True, blank=True)
    telephone_number = models.CharField(max_length=255, null=True, blank=True)

    first_norm = models.CharField(max_length=255, null=True, blank=True)
    last_norm = models.CharField(max_length=255, null=True, blank=True)
    nrn_norm = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('nrn', 'year')

    def __str__(self):
        return f"{self.first_name} {self.surname} ({self.nrn})"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_start_date = models.DateField(null=True, blank=True)
    access_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username