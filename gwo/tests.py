from django.test import TestCase


class gwoTest(TestCase):
    """
    Tests for django-gwo
    """
    def test_gwoExperimentForm(self):
        """
        Make sure the various validations work correctly
        """
        from forms import GwoExperimentForm
        from django.template.loader import render_to_string
        
        test_data = {
            'slug': 'test_1',
            'experiment_id': '',
            'control_script': render_to_string(
                'gwo/gwo_control_script.html', 
                {'experiment': {'experiment_id': 123456}}),
            'tracking_script': render_to_string(
                'gwo/gwo_tracking_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            ),
            'conversion_script': render_to_string(
                'gwo/gwo_conversion_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            )
        }
        
        gwoform = GwoExperimentForm(test_data)
        self.assertTrue(gwoform.is_valid())
        self.assertEqual(gwoform.cleaned_data['experiment_id'], '123456')
        
        test_data = {
            'slug': 'test_2',
            'experiment_id': '',
            'control_script': render_to_string(
                'gwo/gwo_control_script.html', 
                {'experiment': {'experiment_id': 123456}}),
            'tracking_script': render_to_string(
                'gwo/gwo_tracking_script.html',
                {'experiment': {'experiment_id': 12345, 'gwo_account': 654321}}
            ),
            'conversion_script': render_to_string(
                'gwo/gwo_conversion_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            )
        }
        gwoform = GwoExperimentForm(test_data)
        self.assertFalse(gwoform.is_valid())
        
        test_data = {
            'slug': 'test_3',
            'experiment_id': '',
            'control_script': render_to_string(
                'gwo/gwo_control_script.html', 
                {'experiment': {'experiment_id': 12345}}),
            'tracking_script': render_to_string(
                'gwo/gwo_tracking_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            ),
            'conversion_script': render_to_string(
                'gwo/gwo_conversion_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            )
        }
        
        gwoform = GwoExperimentForm(test_data)
        self.assertFalse(gwoform.is_valid())
        
        test_data = {
            'slug': 'test_4',
            'experiment_id': '',
            'control_script': render_to_string(
                'gwo/gwo_control_script.html', 
                {'experiment': {'experiment_id': 123456}}),
            'tracking_script': render_to_string(
                'gwo/gwo_tracking_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            ),
            'conversion_script': render_to_string(
                'gwo/gwo_conversion_script.html',
                {'experiment': {'experiment_id': 123455, 'gwo_account': 654321}}
            )
        }
        
        gwoform = GwoExperimentForm(test_data)
        self.assertFalse(gwoform.is_valid())
    
    def test_TemplateTags(self):
        """
        Make sure the template tags work as expected
        """
        from forms import GwoExperimentForm
        from models import GwoExperiment
        from django.template.loader import render_to_string
        from django.template import Template, Context
        
        test_data = {
            'slug': 'test_1',
            'experiment_id': '',
            'control_script': render_to_string(
                'gwo/gwo_control_script.html', 
                {'experiment': {'experiment_id': 123456}}),
            'tracking_script': render_to_string(
                'gwo/gwo_tracking_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            ),
            'conversion_script': render_to_string(
                'gwo/gwo_conversion_script.html',
                {'experiment': {'experiment_id': 123456, 'gwo_account': 654321}}
            )
        }
        
        gwoform = GwoExperimentForm(test_data)
        self.assertTrue(gwoform.is_valid())
        gwo = gwoform.save()
        
        tmpl = "{% load gwo_tags %}{% gwo_control_script test_1 %}"
        print Template(tmpl).render(Context({}))
        