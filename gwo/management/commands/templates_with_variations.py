import re

from django.core.management.base import BaseCommand, CommandError
from django.template import BLOCK_TAG_START, BLOCK_TAG_END
from django.template.loader import find_template

from generate_variation import TAG_RE

"""
Get the template

1. Look for gwo tags
1a. Flag if they exist
2. Look for includes
3. For each include: call 1 with the template
"""

class Command(BaseCommand):
    help = "Find templates included with the passed template that have GWO tags."
    can_import_settings = True
    args = "<template name>"
    
    @property
    def client(self):
        from gwo.settings import GWO_PASSWORD, GWO_USER
        
        if not hasattr(self, "_client"):
            gwo_client = client.WebsiteOptimizerClient()
            gwo_client.ClientLogin(GWO_USER, GWO_PASSWORD, 'django-gwo')
            self._client = gwo_client
        
        return self._client
    
    def has_gwo_tags(self, template):
        """
        Return True if the template contains django-gwo tags
        """
        return (TAG_RE.search(template) is not None)
    
    def get_included_templates(self, template):
        """
        Return a list of templates included
        """
        include_re = re.compile('%s\\s*include\s+(.*?)\s*%s' % (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END)))
        results = include_re.findall(template)
        return results or []
    
    def process_templates(self, tmpl_list):
        """
        Return a list of templates with variations
        """
        flagged_tmpls = []
        
        for template_name in tmpl_list:
            tmpl, origin = find_template(template_name)
            if self.has_gwo_tags(tmpl):
                flagged_tmpls.append(template_name)
            
            inc_tmpl = self.get_included_templates(tmpl)
            flagged_tmpls.extend(self.process_templates(inc_tmpl))
        return flagged_tmpls
    
    def handle(self, *args, **kwargs):
        results = self.process_templates(args)
        print ""
        print "Templates with variation tags:"
        print "------------------------------"
        if not results:
            print "No tags found"
        for item in results:
            print item
    