from django.contrib import admin
from .models import Member, Address, Country, Gender


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'resident',
                    'line_1',
                    'line_2',
                    'town',
                    'postcode',
                    'country',
                    'active')

admin.site.register(Gender)
admin.site.register(Member)
admin.site.register(Address, AddressAdmin)
admin.site.register(Country)    
