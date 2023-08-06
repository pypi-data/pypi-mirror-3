from django.contrib.admin import ModelAdmin


class GeopositionAdmin(ModelAdmin):
    class Media:
        js = ('geoposition/geoposition.js',)
        css = {
            'all': ('geoposition/geoposition.css',)
        }
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        try:
            print db_field.__slotnames__
            import pdb; pdb.set_trace()
        except:
            pass
        return super(GeopositionAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        