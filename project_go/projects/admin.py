from django.contrib import admin
from .models import Status, Category, Project, Pledge, Reward, UserPledge

admin.site.register(Status)
admin.site.register(Category)
admin.site.register(Project)
admin.site.register(Pledge)
admin.site.register(Reward)
admin.site.register(UserPledge)
