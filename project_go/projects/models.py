from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg

class Status(models.Model):
    status = models.CharField(max_length=100)
    
    def __str__(self):
        return self.status     
    
class Category(models.Model):
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return self.category     

class Project(models.Model):
    owner = models.ForeignKey(User, blank = False)
    title = models.CharField(max_length=100, unique = True)
    goal = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='project_images/%Y-%m/%d')
    short_desc = models.CharField(max_length=200)
    long_desc = models.TextField()
    status = models.ForeignKey(Status, blank = False)
    category = models.ForeignKey(Category, blank = False)
    
    def __str__(self):
        return self.title
    
    def is_funded(self):
        p = Pledge.objects.filter(project=self.id)
        up = UserPledge.objects.filter(id__in=p)
        result = up.aggregate(Sum('amount'))
        return SUM
    
class Reward(models.Model):
    project = models.ForeignKey(Project, blank = False)
    desc = models.CharField(max_length=200, blank = False)
    
    def __str__(self):
        return self.desc
    
class Pledge(models.Model):
    project = models.ForeignKey(Project, blank = False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    rewards = models.ManyToManyField(Reward)

class UserPledge(models.Model):
    user = models.ForeignKey(User, blank = False)
    pledge = models.ForeignKey(Pledge, blank = False)