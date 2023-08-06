from django.contrib import admin
from ccstraps.models import Strap, StrapImage
from ccstraps.forms import StrapAdminForm


class StrapImageInline(admin.TabularInline):
    model = StrapImage


class StrapAdmin(admin.ModelAdmin):
    inlines = [
            StrapImageInline]
    form = StrapAdminForm
    fieldsets = (
        (None, {
            'fields': ( 'name',
                        'delay'),
            'classes': ('main',)
        }),
    )

admin.site.register(Strap, StrapAdmin)
