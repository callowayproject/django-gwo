from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse

from models import GwoExperiment, GwoSection, GwoVariation

def view_experiment(obj):
    """
    Show link to the source experiment
    """
    from django.core.urlresolvers import reverse
    admin_path = reverse("admin:gwo_gwoexperiment_change", args=(obj.gwo_experiment.pk,))
    return '<a href="%s" class="linkbutton">View experiment</a>' % admin_path
view_experiment.allow_tags = True
view_experiment.short_description = 'Experiment'

def view_sections(obj):
    if obj.experiment_type == 'Multivariate':
        num_sections = obj.gwosection_set.count()
        if num_sections == 1:
            response = ["%s section" % num_sections]
        else:
            response = ['%s sections' % num_sections]
        admin_path = reverse("admin:gwo_gwosection_changelist")
        response.append('<a href="%s?gwo_experiment__id__exact=%s" class="linkbutton">View</a>' % (admin_path, obj.id))
    else:
        pass
    return "&nbsp;|&nbsp;".join(response)
view_sections.allow_tags = True
view_sections.short_description = 'Sections'

def add_section(obj):
    """
    Show button for the creation of sections/page variations
    """
    if obj.experiment_type == 'Multivariate':
        admin_path = reverse("admin:gwo_gwosection_add")
        return '<a href="%s?gwo_experiment=%s" class="linkbutton">Add section</a>' % (admin_path, obj.id)
    else:
        return ''
add_section.allow_tags = True
add_section.short_description = 'Add Section'

def sections(obj):
    parts = [view_sections(obj), add_section(obj)]
    return '&nbsp;|&nbsp;'.join(parts)
sections.allow_tags = True

def view_variations(obj):
    """
    Show number of variations, view and add links
    """
    response = []
    num_variations = obj.gwovariation_set.count()
    if num_variations == 1:
        response.append("%s variation" % num_variations)
    else:
        response.append('%s variations' % num_variations)
    admin_path = reverse("admin:gwo_gwovariation_changelist")
    response.append('<a href="%s" class="linkbutton">View</a>' % admin_path)
    
    return "&nbsp;|&nbsp;".join(response)
view_variations.allow_tags = True

def add_variation(obj):
    """
    """
    admin_path = reverse("admin:gwo_gwovariation_add")
    return '<a href="%s?gwo_section=%s&amp;gwo_experiment=%s" class="linkbutton">Add variation</a>' % (admin_path, obj.id, obj.gwo_experiment.id)
add_variation.allow_tags = True

def variations(obj):
    parts = [view_variations(obj), add_variation(obj)]
    return '&nbsp;|&nbsp;'.join(parts)
variations.allow_tags = True

class GwoSectionInlineAdmin(admin.TabularInline):
    model = GwoSection
    fields = ('title')


class GwoExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'experiment_type', 'status', sections)
    list_filter = ('status', 'experiment_type')
    search_fields = ('title',)
    read_only_fields = ('control_script', 'tracking_script', 'conversion_script', 'status', 'report_url', 'configuration_url', 'experiment_id')
    fieldsets = (
        (None, {
            'fields': ('title', 'experiment_type', 'test_url', 'goal_url', 'auto_prune_mode')
        }),
        ('Extra Information', {
            'fields': ('status', 'report_url', 'configuration_url', 'experiment_id', 'control_script', 'tracking_script', 'conversion_script',),
            'classes': ('collapse',)
        })
    )
    add_fieldsets = (
        (None, {
            'fields': ('title', 'experiment_type', 'test_url', 'goal_url', 'auto_prune_mode')
        }),
    )
    #inlines = [GwoSectionInlineAdmin,]
    
    def get_fieldsets(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_fieldsets
        return super(GwoExperimentAdmin, self).get_fieldsets(request, obj, **kwargs)

admin.site.register(GwoExperiment, GwoExperimentAdmin)

class GwoSectionAdmin(admin.ModelAdmin):
    list_display = ('gwo_experiment', 'title', view_experiment, variations)
    search_fields = ('title',)
    read_only_fields = ('section_id',)
    fieldsets = ((None, {'fields': ('gwo_experiment', 'title', 'section_id')}),)
    add_fieldsets = ((None, {'fields': ('gwo_experiment', 'title')}),)
    
    def lookup_allowed(self, lookup):
        if lookup in ('gwo_experiment__id__exact', 'gwo_experiment__id'):
            return True
        else:
            return super(GwoSectionAdmin, self).lookup_allowed(lookup)
    
    def get_fieldsets(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_fieldsets
        return super(GwoSectionAdmin, self).get_fieldsets(request, obj, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        """
        Add the querystrings into the form url so we can use them if they
        click on "Continue and add another"
        """
        if request.META['QUERY_STRING']:
            form_url = '?%s' % request.META['QUERY_STRING']
        return super(GwoSectionAdmin, self).add_view(request, form_url, extra_context)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Check if they clicked on "Continue and add another" and add any
        passed query strings.
        """
        response = super(GwoSectionAdmin, self).response_add(request, obj, post_url_continue)
        if request.META['QUERY_STRING'] and "_addanother" in request.POST:
            if '?' in response['Location']:
                response['Location'] = '%s&%s' % (response['Location'], request.META['QUERY_STRING'])
            else:
                response['Location'] = '%s?%s' % (response['Location'], request.META['QUERY_STRING'])
        return response

admin.site.register(GwoSection, GwoSectionAdmin)

class GwoVariationAdmin(admin.ModelAdmin):
    list_display = ('gwo_experiment', 'gwo_section', 'title')
    fieldsets = ((None, {'fields': ('gwo_experiment', 'gwo_section', 'title', 'variation_id')}),)
    add_fieldsets = ((None, {'fields': ('gwo_experiment', 'title')}),)
    read_only_fields = ('variation_id',)
    
    def lookup_allowed(self, lookup):
        if lookup in ('gwo_section__id__exact', 'gwo_section__id', 'gwo_experiment__id__exact', 'gwo_experiment__id'):
            return True
        else:
            return super(GwoVariationAdmin, self).lookup_allowed(lookup)
    
    def get_fieldsets(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_fieldsets
        return super(GwoVariationAdmin, self).get_fieldsets(request, obj, **kwargs)
    
    def add_view(self, request, form_url='', extra_context=None):
        if request.META['QUERY_STRING']:
            form_url = '?%s' % request.META['QUERY_STRING']
        return super(GwoVariationAdmin, self).add_view(request, form_url, extra_context)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        response = super(GwoVariationAdmin, self).response_add(request, obj, post_url_continue)
        if request.META['QUERY_STRING'] and "_addanother" in request.POST:
            if '?' in response['Location']:
                response['Location'] = '%s&%s' % (response['Location'], request.META['QUERY_STRING'])
            else:
                response['Location'] = '%s?%s' % (response['Location'], request.META['QUERY_STRING'])
        return response
    
admin.site.register(GwoVariation, GwoVariationAdmin)