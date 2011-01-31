from django.test import TestCase
from django.conf import settings

from models import GwoExperiment, GwoSection, GwoVariation
from websiteoptimizer import client

class gwoTest(TestCase):
    """
    Tests for django-gwo
    """
    experiment = {
        'title': 'TestExperiment',
        'experiment_type': 'Multivariate',
        'test_url': 'http://www.example.com/test',
        'goal_url': 'http://www.example.com/goal',
    }
    sections = [{'title':'Section 1'},]
    variations = [
        {
            'title': 'Original',
            'content': '<div>'
        },{
            'title': 'Variation 1',
            'content': '<div class="hide">'
        }
    ]
    def _get_client(self):
        if not hasattr(self, 'gwo_client'):
            self.gwo_client = client.WebsiteOptimizerClient()
            self.gwo_client.ClientLogin(settings.GWO_USER, settings.GWO_PASSWORD, 'django-gwo')
        return self.gwo_client
    
    def testCreationDeletion(self):
        exp = GwoExperiment.objects.create(**self.experiment)
        
        assert(exp.experiment_id is not None)
        
        for section in self.sections:
            GwoSection.objects.create(gwo_experiment=exp, **section)
        
        sections = exp.gwosection_set.all()
        for section in sections:
            for variation in self.variations:
                GwoVariation.objects.create(gwo_section=section, gwo_experiment=exp, **variation)
        url = exp.gwo_url
        v_exp = self._get_client().get_experiment(exp.gwo_url)
        exp.delete()
        v_exp = self._get_client().get_experiment(url)
        