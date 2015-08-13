from django.db import models
from django.contrib.auth.models import User
from django.core.validators  import RegexValidator

class Gender(models.Model):
    gender = models.CharField(max_length=25, unique = True)
    
    def __str__(self):
        return self.gender

class Member(models.Model):
    user = models.OneToOneField(User)
    dob = models.DateField('Date of Birth')
    gender = models.ForeignKey(Gender, blank = True, null = True)
    
    def __str__(self):
        return self.user.username   
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique = True)
    
    def __str__(self):
        return self.name       
    
class Address(models.Model):
    resident = models.ForeignKey(User)
    line_1 = models.CharField(max_length=50)
    line_2 = models.CharField(max_length=50, blank = True, null = True)
    town = models.CharField(max_length=50)
    postcode = models.CharField(max_length=10,
                                validators=[ RegexValidator(
                                        regex='^[a-zA-Z][a-zA-Z][0-9][0-9a-zA-Z]?[ |-]?[0-9][a-zA-Z]{2}$',
                                        message='Your postcode was not in the correct format',
                                        code='invalid_postcode'
                                    ),
                                ])
    country = models.ForeignKey(Country)
    active = models.NullBooleanField(blank = True, null = True)
    
    def __str__(self):
        return self.line_1 + ", " + self.line_2 + ", " + self.town + ", " + self.postcode
    
    
    
