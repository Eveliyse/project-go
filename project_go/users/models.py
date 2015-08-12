from django.db import models
from django.contrib.auth.models import User

class Gender(models.Model):
    gender = models.CharField(max_length=25, unique = True)
    
    def __str__(self):
        return self.gender

class Member(models.Model):
    user = models.OneToOneField(User)
    dob = models.DateField('Date of Birth')
    gender = models.ForeignKey(Gender, blank = False)
    
    def __str__(self):
        return self.user.username   
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique = True)
    
    def __str__(self):
        return self.name       
    
class Address(models.Model):
    resident = models.ForeignKey(Member, blank = False)
    line_1 = models.CharField(max_length=50, blank = False)
    line_2 = models.CharField(max_length=50)
    town = models.CharField(max_length=50, blank = False)
    postcode = models.CharField(max_length=10, blank = False)
    country = models.ForeignKey(Country, blank = False)
    
    def __str__(self):
        return self.line_1 + ", " + self.line_2 + ", " + self.town + ", " + self.postcode
    
    
    
