from django.db import models
from django.contrib.auth.models import User


class Member(models.Model):
    user = models.OneToOneField(User)
    dob = models.DateField('Date of Birth')
    
    def __str__(self):
        return self.user.username    
    
class Address(models.Model):
    resident = models.ForeignKey(Member)
    line_1 = models.CharField(max_length=200)
    line_2 = models.CharField(max_length=200)
    town = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    
    def __str__(self):
        return self.line_1 + ", " + self.line_2 + ", " + self.town + ", " + self.postcode