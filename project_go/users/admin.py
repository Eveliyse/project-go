from django.contrib import admin
from .models import Member, Address, Country

admin.site.register(Member)
admin.site.register(Address)
admin.site.register(Country)
