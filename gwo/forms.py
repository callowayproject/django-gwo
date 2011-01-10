import re

from django import forms
from django.template.loader import render_to_string

from models import GwoExperiment
import settings

class GwoExperimentForm(forms.ModelForm):
    """
    A form for a Google Web Experiment with extra validation
    
    1. If experiment id is specified, set the scripts based on the templates
       for each script (unless the script has also been specified)
    2. If one or more scripts is specified, pull the experiment id out of the
       script
    3. Make sure that none of the experiment ids conflict from the various 
       places they could originate
    4. Set the experiment id, as long as there are no conflicts
    """
    control_script_re = re.compile(r'k=[\'"](\d+)[\'"]')
    tracking_script_re = re.compile(r'_trackPageview\("/(\d+)/test"\)')
    conversion_script_re = re.compile(r'_trackPageview\("/(\d+)/goal"\)')
    
    class Meta:
        model = GwoExperiment
    
    def clean_control_script(self):
        """
        Extract the experiment id from the script and make sure it doesn't 
        conflict with the current eperiment id field, and set experiement id
        field if it is blank
        """
        control_script = self.cleaned_data['control_script']
        cur_exp_id = self.cleaned_data.get('experiment_id', None)
        if control_script:
            search_result = self.control_script_re.search(control_script)
            if search_result:
                exp_id = search_result.groups()[0]
            else:
                exp_id = None
            if exp_id and not cur_exp_id:
                self.cleaned_data['experiment_id'] = exp_id
            elif exp_id and exp_id != cur_exp_id:
                raise forms.ValidationError("The GWO experiment id in the Control Script doesn't match the experiment id specified in one of the other fields.")
            return control_script
        elif 'experiment_id' in self.cleaned_data:
            return render_to_string(
                "gwo/gwo_control_script.html", 
                {
                    'experiment': self.cleaned_data, 
                    'gwo_account': settings.GWO_ACCOUNT
                }
            )
        else:
            raise forms.ValidationError("The Control Script field is required.")
    
    def clean_tracking_script(self):
        """
        Extract the experiment id from the script and make sure it doesn't 
        conflict with the current eperiment id field, and set experiement id
        field if it is blank
        """
        tracking_script = self.cleaned_data['tracking_script']
        cur_exp_id = self.cleaned_data.get('experiment_id', None)
        if tracking_script:
            search_result = self.tracking_script_re.search(tracking_script)
            if search_result:
                exp_id = search_result.groups()[0]
            else:
                exp_id = None
            if exp_id and not cur_exp_id:
                self.cleaned_data['experiment_id'] = exp_id
            elif exp_id and exp_id != cur_exp_id:
                raise forms.ValidationError("The GWO experiment id in the Tracking Script doesn't match the experiment id specified in one of the other fields.")
            return tracking_script
        elif 'experiment_id' in self.cleaned_data:
            return render_to_string(
                "gwo/gwo_tracking_script.html", 
                {
                    'experiment': self.cleaned_data,
                    'gwo_account': settings.GWO_ACCOUNT,
                }
            )
        else:
            raise forms.ValidationError("The Tracking Script field is required.")
    
    def clean_conversion_script(self):
        """
        Extract the experiment id from the script and make sure it doesn't 
        conflict with the current eperiment id field, and set experiement id
        field if it is blank
        """
        conversion_script = self.cleaned_data['conversion_script']
        cur_exp_id = self.cleaned_data.get('experiment_id', None)
        if conversion_script:
            search_result = self.conversion_script_re.search(conversion_script)
            if search_result:
                exp_id = search_result.groups()[0]
            else:
                exp_id = None
            if exp_id and not cur_exp_id:
                self.cleaned_data['experiment_id'] = exp_id
            elif exp_id and exp_id != cur_exp_id:
                raise forms.ValidationError("The GWO experiment id in the Conversion Script doesn't match the experiment id specified in one of the other fields.")
            return conversion_script
        elif 'experiment_id' in self.cleaned_data:
            return render_to_string(
                "gwo/gwo_conversion_script.html", 
                {
                    'experiment': self.cleaned_data,
                    'gwo_account': settings.GWO_ACCOUNT,
                }
            )
        else:
            raise forms.ValidationError("The Conversion Script field is required.")
        