from django.contrib import admin
from django.utils.translation import ugettext as _

from metro_tiny.models import MetroLine, MetroStation

class MetroStationInline(admin.TabularInline):
    model = MetroStation

class MetroLineAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city__name')
    raw_id_fields = ('city',)
    inlines = (MetroStationInline,)
    save_on_top = True

admin.site.register(MetroLine, MetroLineAdmin)

class MetroStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_city', 'line')
    search_fields = ('name', 'line__city__name')
    raw_id_fields = ('line',)
    readonly_fields = ('display_city',)

    def display_city(self, obj):
	return obj.line.city
    display_city.admin_order_field = 'line__city'
    display_city.short_description = _("City")

admin.site.register(MetroStation, MetroStationAdmin)
