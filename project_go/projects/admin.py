from django.contrib import admin
from .models import Status, Category, Project, Pledge, Reward, UserPledge

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'goal', 'status', 'category', 'pledged_amount', 'pledged_percent', 'is_funded', 'pledgers', 'created_date')

admin.site.register(Status)
admin.site.register(Category)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Pledge)
admin.site.register(Reward)
admin.site.register(UserPledge)

