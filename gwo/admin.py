from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import (HttpResponseNotAllowed, HttpResponseRedirect,
                        HttpResponseForbidden)
from django.shortcuts import get_object_or_404

from models import GwoExperiment, GwoSection, GwoVariation

def view_experiment(obj):
    """
    Show link to the source experiment
    """
    admin_path = reverse(
        "admin:gwo_gwoexperiment_change", 
        args=(obj.gwo_experiment.pk,))
    return '<a href="%s" class="linkbutton">%s (View)</a>' % \
            (admin_path, obj.gwo_experiment.title)
view_experiment.allow_tags = True
view_experiment.short_description = 'Experiment'

def view_sections(obj):
    """
    Show the number of sections on an experiment and a link to view them
    """
    if obj.experiment_type == 'Multivariate':
        num_sections = obj.gwosection_set.count()
        if num_sections == 1:
            response = ["%s section" % num_sections]
        else:
            response = ['%s sections' % num_sections]
        admin_path = reverse("admin:gwo_gwosection_changelist")
        response.append(''.join([
            '<a href="%s' % admin_path,
            '?gwo_experiment__id__exact=%s" ' % obj.id,
            'class="linkbutton">View</a>']))
        return "&nbsp;|&nbsp;".join(response)
    return ''
view_sections.allow_tags = True
view_sections.short_description = 'Sections'

def view_section(obj):
    """
    Show the related section name and link to it
    """
    admin_path = reverse(
        "admin:gwo_gwosection_change", 
        args=(obj.gwo_section.pk,))
    return '<a href="%s" class="linkbutton">%s (View)</a>' \
            % (admin_path, obj.gwo_section.title)
view_section.allow_tags = True
view_section.short_description = 'Section'

def add_section(obj):
    """
    Show button for the creation of sections 
    (if experiment type is multivariate)
    """
    if obj.experiment_type == 'Multivariate':
        admin_path = reverse("admin:gwo_gwosection_add")
        return ''.join([
            '<a href="%s' % admin_path,
            '?gwo_experiment=%s" ' % obj.id,
            'class="linkbutton">Add section</a>'])
    return ''
add_section.allow_tags = True
add_section.short_description = 'Add Section'

def sections(obj):
    """
    Combination of the view_sections and add_section to put it all in one field
    """
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
    response.append(''.join([
        '<a href="%s' % admin_path,
        '?gwo_experiment__id__exact=%s' % obj.gwo_experiment.id,
        '&amp;gwo_section__id__exact=%s' % obj.id,
        '" class="linkbutton">View</a>']))
    
    return "&nbsp;|&nbsp;".join(response)
view_variations.allow_tags = True

def add_variation(obj):
    """
    Add a variation to a section
    """
    admin_path = reverse("admin:gwo_gwovariation_add")
    return ''.join([
        '<a href="%s' % admin_path,
        '?gwo_section=%s' % obj.id,
        '&amp;gwo_experiment=%s" ' % obj.gwo_experiment.id,
        'class="linkbutton">Add variation</a>'])
add_variation.allow_tags = True

def variations(obj):
    parts = [view_variations(obj), add_variation(obj)]
    return '&nbsp;|&nbsp;'.join(parts)
variations.allow_tags = True


class GwoExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'experiment_type', 'status_links', sections)
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
    def status_links(self, obj):
        """
        Color the status and add start/stop/pause links/buttons
        """
        from django.template.loader import render_to_string
        from django.template import RequestContext
        colors = {
            'New': '#00F',
            'Running': '#0F0',
            'Paused': '#F00',
            'Finished': '#000'
        }
        links = render_to_string('admin/gwo/status_links.html', {'obj': obj})
        return '<strong style="color:%s">%s</strong>&nbsp;%s' % (colors[obj.status], obj.status, links)
    status_links.allow_tags=True
    status_links.short_description='Status'
    status_links.admin_order_field='status'
    
    def get_urls(self):
        """
        Add the set_status URL for starting/pausing/finishing experiments
        """
        from django.conf.urls.defaults import patterns
        
        urls = super(GwoExperimentAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(?P<id>\d+)/set_status/$', self.admin_site.admin_view(self.set_status)),
        )
        return my_urls + urls
    
    def set_status(self, request, id):
        """
        Takes a POST to set the status of the experiment
        """
        from gwo.websiteoptimizer import client
        from django.conf import settings
        
        gwo_client = client.WebsiteOptimizerClient()
        gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        
        status_methods = {
            'Running': gwo_client.start_experiment,
            'Paused': gwo_client.pause_experiment,
            'Finished': gwo_client.stop_experiment
        }
        
        # If at some time I figure out how to POST from the changelist without
        # using the actions, I will go back to this preferred method. Until
        # that time, I'll have to use GET
        # if request.method != 'POST':
        #     return HttpResponseNotAllowed(['POST',])
        
        exp = get_object_or_404(GwoExperiment, pk=id)
        
        status = request.REQUEST['status']
        if status not in status_methods:
            return HttpResponseForbidden()
        
        if 'HTTP_REFERER' in request.META and request.META['HTTP_REFERER']:
            dest_url = request.META['HTTP_REFERER']
        else:
            dest_url = reverse('admin:gwo_gwoexperiment_changelist')
        
        
        gwo_exp = status_methods[status](client.ExperimentQuery(exp.experiment_id))
        exp.status = gwo_exp.status.text
        exp.save(local_only=True)
        return HttpResponseRedirect(dest_url)
    
    def get_fieldsets(self, request, obj=None, **kwargs):
        if obj is None:
            return self.add_fieldsets
        return super(GwoExperimentAdmin, self).get_fieldsets(request, obj, **kwargs)

admin.site.register(GwoExperiment, GwoExperimentAdmin)

class GwoSectionAdmin(admin.ModelAdmin):
    list_display = ('title', view_experiment, variations)
    search_fields = ('title',)
    read_only_fields = ('section_id',)
    fieldsets = (
        (None, {
            'fields': ('gwo_experiment', 'title',),
        }), (
        'Extra Information', {
            'fields': ('section_id', 'begin_script', 'end_script'),
            'classes': ('collapse',)
        }),
    )
    add_fieldsets = ((None, {'fields': ('gwo_experiment', 'title')}),)
    
    def lookup_allowed(self, lookup):
        if lookup in ('gwo_experiment__id__exact', 'gwo_experiment__id'):
            return True
        else:
            return super(GwoSectionAdmin, self).lookup_allowed(lookup)
    
    def get_fieldsets(self, request, obj=None, **kwargs):
        """
        We return a different set of fieldsets if it is an add operation
        """
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
    list_display = ('title', view_experiment, view_section)
    fieldsets = (
        (None, {
            'fields': ('gwo_experiment', 'gwo_section', 'title', 'content',)
        }), (
        'Extra Information', {
            'fields': ('variation_id',),
            'classes': ('collapse',)
        }),
    )
    add_fieldsets = ((None, {'fields': ('gwo_experiment', 'gwo_section', 'title', 'content')}),)
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