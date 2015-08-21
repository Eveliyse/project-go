from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from decimal import *

class Status(models.Model):
    status = models.CharField(max_length=100)
    
    def __str__(self):
        return self.status     
    
class Category(models.Model):
    category = models.CharField(max_length=100)
    
    def __str__(self):
        return self.category     

class Project(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100, unique = True)
    goal = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='project_images/%Y-%m/%d')
    short_desc = models.CharField(max_length=200)
    long_desc = models.TextField()
    status = models.ForeignKey(Status)
    category = models.ForeignKey(Category)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def pledged_amount(self):
        pledges = Pledge.objects.filter(project = self)
        user_pledges = UserPledge.objects.filter(pledge__in = pledges)
        sum_amount = user_pledges.aggregate(amount=Sum('pledge__amount'))
        result = sum_amount['amount']
        if result is None:
            return format(0.00, '.2f')
        return result

    def pledged_percent(self):
        if self.pledged_amount() is None or self.pledged_amount() == 0:
            return 0
        return format(Decimal(self.pledged_amount()) / Decimal(self.goal) * 100, '.0f')
    
    def pledgers(self):			
        up = UserPledge.objects.filter(pledge__project = self)
        result = up.aggregate(Count('user'))
        return result['user__count']
    
    def is_funded(self):		
        amount = self.pledged_amount()
        return amount >= self.goal      
    
    def __str__(self):
        return self.title + " by " + self.owner.username
    
class Reward(models.Model):
    project = models.ForeignKey(Project)
    desc = models.CharField(max_length=200)
    
    def __str__(self):
        return self.desc
    
class Pledge(models.Model):
    project = models.ForeignKey(Project, related_name='project_pledges')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    rewards = models.ManyToManyField(Reward, blank= True)
    
    def __str__(self):
        rstr = " "
        for reward in self.rewards.all():
            rstr = rstr + reward.desc + ", "
        return self.project.title + " " + str(self.amount) + " " + rstr

class UserPledge(models.Model):
    user = models.ForeignKey(User, related_name='user_pledges')
    pledge = models.ForeignKey(Pledge, related_name='pledged_users')
    
    def __str__(self):
        return self.user.username + ", " + str(self.pledge)