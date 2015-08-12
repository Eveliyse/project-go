from django.contrib import admin
from .models import Member, Address, Country, Gender

admin.site.register(Gender)
admin.site.register(Member)
admin.site.register(Address)
admin.site.register(Country)
