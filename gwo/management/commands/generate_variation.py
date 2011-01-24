import re

from django.core.management.base import BaseCommand, CommandError
from django.template import BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END
from django.template.loader import find_template

from gwo.websiteoptimizer import client
from gwo.models import GwoExperiment, GwoSection, GwoVariation

TAGS = [
    '%s\\s*%s.*?%s' % (re.escape(BLOCK_TAG_START), 'gwo_start_section', re.escape(BLOCK_TAG_END)),
    '%s\\s*%s.*?%s' % (re.escape(BLOCK_TAG_START), 'gwo_end_section', re.escape(BLOCK_TAG_END)),
    '%s\\s*%s.*?%s' % (re.escape(BLOCK_TAG_START), 'set_experiment', re.escape(BLOCK_TAG_END)),
    '%s\\s*%s.*?%s' % (re.escape(VARIABLE_TAG_START), 'gwo_experiment', re.escape(VARIABLE_TAG_END)),
]
TAG_RE = re.compile('(%s)' % ('|'.join(TAGS)))

TOKEN = "".join([
    '(?:',
    re.escape(BLOCK_TAG_START),
    '|',
    re.escape(VARIABLE_TAG_START), 
    r')\s*([a-zA-Z0-9-_]+)\s*(.+?)\s*', 
    '(?:',
    re.escape(VARIABLE_TAG_END),
    '|',
    re.escape(BLOCK_TAG_END),
    ')'
])
TOKEN_RE = re.compile(TOKEN)

class Command(BaseCommand):
    help = "Output the template with the variations for a combination"
    can_import_settings = True
    args = "<template name> <combination number>"
    
    @property
    def client(self):
        from gwo.settings import GWO_PASSWORD, GWO_USER
        
        if not hasattr(self, "_client"):
            gwo_client = client.WebsiteOptimizerClient()
            gwo_client.ClientLogin(GWO_USER, GWO_PASSWORD, 'django-gwo')
            self._client = gwo_client
        
        return self._client
    
    def _fill_variations(self, experiment, combination):
        if not hasattr(self, "_variations"):
            self._variations = {}
        
        if experiment in self._variations:
            return
        else:
            self._variations[experiment] = {}
        exp_id = GwoExperiment.objects.get(title=experiment.strip('"')).experiment_id
        combo = self.client.get_combination(client.CombinationQuery(exp_id, combination))
        
        var_nums = combo.combo_string.text.split("-")
        
        for section, variation in enumerate(var_nums):
            var = GwoVariation.objects.select_related().get(
                variation_id=variation, 
                gwo_section__section_id=section, 
                gwo_experiment__experiment_id=exp_id)
            
            self._variations[experiment][var.gwo_section.title] = var.content
    
    @property
    def variations(self):
        if not hasattr(self, "_variations"):
            raise CommandError('Variations are not set. Missing a set_experiment somewhere.')
        return self._variations
    
    def handle(self, *args, **kwargs):
        template_name, combination = args
        template, origin = find_template(template_name)
        bits = TAG_RE.split(template)
        output = []
        current_exp = None
        current_section = None
        
        for item in bits:
            if TAG_RE.match(item):
                tag, var = TOKEN_RE.match(item).groups()
                if tag == 'gwo_experiment':
                    continue
                elif tag == 'set_experiment':
                    current_exp = var
                    self._fill_variations(current_exp, combination)
                elif tag == 'gwo_start_section':
                    current_section = var.strip('"')
                elif tag == 'gwo_end_section':
                    output.append(self.variations[current_exp][current_section])
                    current_section = None
                else:
                    raise CommandError("Found unrecognized tag: %s" % tag)
            elif current_section is not None:
                continue
            else:
                output.append(item)
        print "".join(output)