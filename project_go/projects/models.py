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
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100, unique = True)
    goal = models.DecimalField(max_digits=12, decimal_places=2)
    image = models.ImageField(upload_to='project_images/%Y-%m/%d')
    short_desc = models.CharField(max_length=200)
    long_desc = models.TextField()
    status = models.ForeignKey(Status)
    category = models.ForeignKey(Category)
    
    def pledged_amount(self):			
        up = UserPledge.objects.filter(pledge__project = self)
        result = up.aggregate(Sum('pledge__amount'))
        return result
    
    def pledgers(self):			
        up = UserPledge.objects.filter(pledge__project = self)
        result = up.aggregate(Count('user'))
        return result    
    
    def is_funded(self):		
        amount = self.pledged_amount()['pledge__amount__sum']
        return amount >= self.goal
    
    def open_project(self):
        up = UserPledge.objects.filter(pledge__project = self)
        if up is not None:
            newStatus = Status.objects.get(status = "New")
            if self.status is newStatus:
                openStatus = Status.objects.get(status = "Open")
                self.status = openStatus
                self.save()
    
    def __str__(self):
        return self.title
    
class Reward(models.Model):
    project = models.ForeignKey(Project)
    desc = models.CharField(max_length=200)
    
    def __str__(self):
        return self.desc
    
class Pledge(models.Model):
    project = models.ForeignKey(Project)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    rewards = models.ManyToManyField(Reward, blank= True)
    
    def __str__(self):
        rstr = " "
        for reward in self.rewards.all():
            rstr = rstr + reward.desc + ", "
        return self.project.title + " " + str(self.amount) + " " + rstr

class UserPledge(models.Model):
    user = models.ForeignKey(User)
    pledge = models.ForeignKey(Pledge)