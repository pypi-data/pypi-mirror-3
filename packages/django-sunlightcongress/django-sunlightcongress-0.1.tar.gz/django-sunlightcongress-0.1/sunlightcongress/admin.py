from django.contrib import admin
from sunlightcongress.models import Legislator


class LegislatorAdmin(admin.ModelAdmin):
    """
    ModelAdmin object for the Legislator model
    """
    list_display = (
        'fullname',
        'party',
        'house',
        'state',
    )
    list_filter = (
        'title',
        'party',
        'in_office',
        'gender',
    )
    search_fields = (
        'firstname',
        'middlename',
        'lastname',
    )

admin.site.register(Legislator, LegislatorAdmin)
